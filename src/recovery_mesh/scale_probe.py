from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from time import perf_counter_ns
from typing import Any

from .graph import TrustGraph
from .hashing import sha256_digest
from .models import (
    Checkpoint,
    CheckpointKind,
    IntegrityMetadata,
    ProvenanceMetadata,
    TrustBreak,
    TrustBreakClass,
    TrustStatus,
)
from .recovery import RecoveryEngine

SCALE_RUN_ID = "scale-probe-100-agents"
SCALE_POLICY_VERSION = "scale-policy-v1"
BRANCH_COUNT = 8
AGENTS_PER_BRANCH = 12
MERGE_AGENT_COUNT = 3
TOTAL_AGENT_COUNT = BRANCH_COUNT * AGENTS_PER_BRANCH + MERGE_AGENT_COUNT + 1


@dataclass(frozen=True)
class ScaleProbeReceipt:
    run_id: str
    synthetic_agent_checkpoints: int
    total_checkpoints: int
    fault_checkpoint: str
    affected_agent_checkpoints: int
    reused_agent_checkpoints: int
    blocked_action_nodes: int
    planning_elapsed_us: int
    affected_agent_ratio: float
    reused_agent_ratio: float
    measurement_class: str = "deterministic_synthetic_scale_probe"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _checkpoint(
    checkpoint_id: str,
    *,
    kind: CheckpointKind,
    dependencies: tuple[str, ...],
    existing: dict[str, Checkpoint],
    agent_id: str | None = None,
    side_effect_key: str | None = None,
) -> Checkpoint:
    output = {"checkpoint_id": checkpoint_id, "kind": kind.value, "synthetic": True}
    digest = sha256_digest(output)
    now = datetime.now(UTC)
    return Checkpoint(
        run_id=SCALE_RUN_ID,
        checkpoint_id=checkpoint_id,
        kind=kind,
        agent_id=agent_id,
        agent_version="scale-probe-v1" if agent_id else None,
        dependency_checkpoint_ids=dependencies,
        input_digests=tuple(existing[item].structured_output_digest for item in dependencies),
        evidence_digests=tuple(
            existing[item].structured_output_digest
            for item in dependencies
            if existing[item].kind is CheckpointKind.EVIDENCE
        ),
        tool_result_digests=(),
        policy_version=SCALE_POLICY_VERSION,
        structured_output_digest=digest,
        verification_status=TrustStatus.VERIFIED,
        integrity=IntegrityMetadata(digest=digest),
        provenance=ProvenanceMetadata(
            source_class="controlled_scale_fixture",
            source_ref=f"controlled://scale/{checkpoint_id}",
            observed_at=now,
            controlled_fixture=True,
        ),
        created_at=now,
        verified_at=now,
        side_effect_key=side_effect_key,
        metadata={"synthetic_scale_probe": True},
    )


def build_synthetic_100_agent_fleet() -> tuple[Checkpoint, ...]:
    """Build 100 synthetic AGENT checkpoints without making model calls.

    The graph has eight independent 12-agent branches, three merge agents, one root
    orchestrator, evidence sources, one policy node, and one final action. It exists only
    to prove deterministic blast-radius/reuse behavior at fleet scale.
    """
    checkpoints: dict[str, Checkpoint] = {}

    for branch in range(BRANCH_COUNT):
        source_id = f"source_{branch}"
        checkpoints[source_id] = _checkpoint(
            source_id,
            kind=CheckpointKind.EVIDENCE,
            dependencies=(),
            existing=checkpoints,
        )

    checkpoints["policy_rules"] = _checkpoint(
        "policy_rules",
        kind=CheckpointKind.POLICY,
        dependencies=(),
        existing=checkpoints,
    )

    branch_tails: list[str] = []
    for branch in range(BRANCH_COUNT):
        parent = f"source_{branch}"
        for depth in range(AGENTS_PER_BRANCH):
            agent_id = f"branch_{branch}_agent_{depth:02d}"
            checkpoints[agent_id] = _checkpoint(
                agent_id,
                kind=CheckpointKind.AGENT,
                dependencies=(parent,),
                existing=checkpoints,
                agent_id=agent_id,
            )
            parent = agent_id
        branch_tails.append(parent)

    merge_dependencies = (
        tuple(branch_tails[0:3]),
        tuple(branch_tails[3:6]),
        tuple(branch_tails[6:8]),
    )
    merge_ids: list[str] = []
    for index, dependencies in enumerate(merge_dependencies):
        merge_id = f"merge_agent_{index}"
        checkpoints[merge_id] = _checkpoint(
            merge_id,
            kind=CheckpointKind.AGENT,
            dependencies=dependencies,
            existing=checkpoints,
            agent_id=merge_id,
        )
        merge_ids.append(merge_id)

    checkpoints["root_orchestrator"] = _checkpoint(
        "root_orchestrator",
        kind=CheckpointKind.AGENT,
        dependencies=(*merge_ids, "policy_rules"),
        existing=checkpoints,
        agent_id="root_orchestrator",
    )
    checkpoints["publish_action"] = _checkpoint(
        "publish_action",
        kind=CheckpointKind.ACTION,
        dependencies=("root_orchestrator",),
        existing=checkpoints,
        side_effect_key=f"{SCALE_RUN_ID}:publish",
    )

    agent_count = sum(1 for item in checkpoints.values() if item.kind is CheckpointKind.AGENT)
    if agent_count != TOTAL_AGENT_COUNT:
        raise RuntimeError(f"scale probe expected {TOTAL_AGENT_COUNT} agents, got {agent_count}")
    return tuple(checkpoints.values())


def run_scale_probe(fault_checkpoint: str = "source_0") -> ScaleProbeReceipt:
    graph = TrustGraph(build_synthetic_100_agent_fleet())
    trust_break = TrustBreak(
        break_id=f"scale-break:{fault_checkpoint}",
        run_id=SCALE_RUN_ID,
        checkpoint_id=fault_checkpoint,
        break_class=TrustBreakClass.EVIDENCE,
        reason_code="CONTROLLED_SCALE_PROBE",
        reason="Synthetic scale-probe trust break; no model call or production data involved.",
        controlled=True,
    )

    start = perf_counter_ns()
    plan = RecoveryEngine(graph).plan(trust_break)
    planning_elapsed_us = max(1, (perf_counter_ns() - start) // 1_000)

    affected_agents = sum(
        1
        for checkpoint_id in plan.blast_radius.recomputation_set
        if graph.checkpoint(checkpoint_id).kind is CheckpointKind.AGENT
    )
    reused_agents = sum(
        1
        for checkpoint_id in plan.blast_radius.reusable_checkpoints
        if graph.checkpoint(checkpoint_id).kind is CheckpointKind.AGENT
    )
    return ScaleProbeReceipt(
        run_id=SCALE_RUN_ID,
        synthetic_agent_checkpoints=TOTAL_AGENT_COUNT,
        total_checkpoints=len(graph.checkpoints),
        fault_checkpoint=fault_checkpoint,
        affected_agent_checkpoints=affected_agents,
        reused_agent_checkpoints=reused_agents,
        blocked_action_nodes=len(plan.blast_radius.blocked_action_nodes),
        planning_elapsed_us=planning_elapsed_us,
        affected_agent_ratio=affected_agents / TOTAL_AGENT_COUNT,
        reused_agent_ratio=reused_agents / TOTAL_AGENT_COUNT,
    )
