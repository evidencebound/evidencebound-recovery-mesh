from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from .hashing import sha256_digest
from .models import (
    Checkpoint,
    CheckpointKind,
    IntegrityMetadata,
    ProvenanceMetadata,
    TrustStatus,
)

RUN_ID = "judge-demo-001"
POLICY_VERSION = "policy-v1"
AGENT_ORDER = ("statistician", "scout", "skeptic", "orchestrator")
AGENT_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "statistician": ("fixture_snapshot", "history_snapshot"),
    "scout": ("fixture_snapshot",),
    "skeptic": ("statistician", "scout"),
    "orchestrator": ("statistician", "scout", "skeptic", "policy_rules"),
}


def baseline_source_outputs() -> dict[str, Any]:
    return {
        "fixture_snapshot": {
            "fixture": "Northport FC vs Lakeside FC",
            "status": "pre-match",
            "fixture_id": "controlled-fixture-001",
        },
        "history_snapshot": {
            "sample_size": 18,
            "metric": "recent-form",
            "window": "controlled-history-v1",
        },
        "policy_rules": {
            "policy_version": POLICY_VERSION,
            "require_citations": True,
            "allow_publish_only_if_verified": True,
        },
        "statistician": {
            "claim": "bounded quantitative signal",
            "evidence_ids": ["fixture_snapshot", "history_snapshot"],
            "confidence": 0.62,
        },
        "scout": {
            "claim": "bounded context signal",
            "evidence_ids": ["fixture_snapshot"],
            "confidence": 0.58,
        },
        "skeptic": {
            "claim": "challenge unsupported certainty",
            "evidence_ids": ["statistician", "scout"],
            "confidence": 0.71,
        },
        "orchestrator": {
            "claim": "provisional research verdict",
            "evidence_ids": ["statistician", "scout", "skeptic"],
            "confidence": 0.64,
        },
        "publish_action": {"published": True},
    }


def build_agent_prompt(checkpoint_id: str, outputs: Mapping[str, Any]) -> str:
    dependencies = AGENT_DEPENDENCIES[checkpoint_id]
    bounded_inputs = {dependency: outputs[dependency] for dependency in dependencies}
    return (
        "EvidenceBound Recovery Mesh controlled judge workload.\n"
        f"Checkpoint: {checkpoint_id}\n"
        "Use only the bounded JSON inputs below. Do not infer external facts.\n"
        "Return exactly one compact JSON object; no markdown.\n"
        f"DEPENDENCY_CHECKPOINT_IDS={json.dumps(list(dependencies), separators=(',', ':'))}\n"
        "For evidence_ids, cite only those dependency checkpoint IDs; never cite nested raw "
        "field values such as fixture_id or window.\n"
        f"INPUTS={json.dumps(bounded_inputs, sort_keys=True, separators=(',', ':'))}"
    )


def _checkpoint(
    checkpoint_id: str,
    *,
    run_id: str,
    kind: CheckpointKind,
    output: Any,
    dependencies: tuple[str, ...] = (),
    dependency_checkpoints: Mapping[str, Checkpoint],
    agent_id: str | None = None,
    agent_version: str | None = None,
    source_class: str,
    source_ref: str | None = None,
    controlled_fixture: bool = False,
    side_effect_key: str | None = None,
    policy_version: str = POLICY_VERSION,
    metadata: dict[str, Any] | None = None,
) -> Checkpoint:
    digest = sha256_digest(output)
    now = datetime.now(UTC)
    input_digests = tuple(
        dependency_checkpoints[dependency].structured_output_digest for dependency in dependencies
    )
    evidence_digests = tuple(
        dependency_checkpoints[dependency].structured_output_digest
        for dependency in dependencies
        if dependency_checkpoints[dependency].kind is CheckpointKind.EVIDENCE
    )
    return Checkpoint(
        run_id=run_id,
        checkpoint_id=checkpoint_id,
        kind=kind,
        agent_id=agent_id,
        agent_version=agent_version,
        dependency_checkpoint_ids=dependencies,
        input_digests=input_digests,
        evidence_digests=evidence_digests,
        tool_result_digests=(),
        policy_version=policy_version,
        structured_output_digest=digest,
        verification_status=TrustStatus.VERIFIED,
        integrity=IntegrityMetadata(digest=digest),
        provenance=ProvenanceMetadata(
            source_class=source_class,
            source_ref=source_ref,
            observed_at=now,
            controlled_fixture=controlled_fixture,
        ),
        created_at=now,
        verified_at=now,
        side_effect_key=side_effect_key,
        metadata=metadata or {},
    )


def build_demo_checkpoints(
    run_id: str = RUN_ID,
    *,
    outputs: Mapping[str, Any] | None = None,
    agent_provenance: Mapping[str, Mapping[str, Any]] | None = None,
    policy_version: str = POLICY_VERSION,
) -> tuple[Checkpoint, ...]:
    """Build the bounded clean-room DAG with digests bound to actual parent outputs."""
    effective_outputs = baseline_source_outputs()
    if outputs:
        effective_outputs.update(outputs)
    provenance = agent_provenance or {}
    checkpoints: dict[str, Checkpoint] = {}

    checkpoints["fixture_snapshot"] = _checkpoint(
        "fixture_snapshot",
        run_id=run_id,
        kind=CheckpointKind.EVIDENCE,
        output=effective_outputs["fixture_snapshot"],
        dependency_checkpoints=checkpoints,
        source_class="controlled_fixture",
        source_ref="controlled://fixture_snapshot",
        controlled_fixture=True,
        policy_version=policy_version,
    )
    checkpoints["history_snapshot"] = _checkpoint(
        "history_snapshot",
        run_id=run_id,
        kind=CheckpointKind.EVIDENCE,
        output=effective_outputs["history_snapshot"],
        dependency_checkpoints=checkpoints,
        source_class="controlled_fixture",
        source_ref="controlled://history_snapshot",
        controlled_fixture=True,
        policy_version=policy_version,
    )
    checkpoints["policy_rules"] = _checkpoint(
        "policy_rules",
        run_id=run_id,
        kind=CheckpointKind.POLICY,
        output=effective_outputs["policy_rules"],
        dependency_checkpoints=checkpoints,
        source_class="deterministic_policy",
        source_ref=f"policy://{policy_version}",
        policy_version=policy_version,
    )

    for agent_id in AGENT_ORDER:
        agent_info = provenance.get(agent_id, {})
        checkpoints[agent_id] = _checkpoint(
            agent_id,
            run_id=run_id,
            kind=CheckpointKind.AGENT,
            output=effective_outputs[agent_id],
            dependencies=AGENT_DEPENDENCIES[agent_id],
            dependency_checkpoints=checkpoints,
            agent_id=agent_id,
            agent_version=str(agent_info.get("agent_version", "hackathon-v1")),
            source_class=str(agent_info.get("source_class", "deterministic_test")),
            source_ref=(
                str(agent_info["source_ref"]) if agent_info.get("source_ref") is not None else None
            ),
            policy_version=policy_version,
            metadata=dict(agent_info.get("metadata", {})),
        )

    checkpoints["publish_action"] = _checkpoint(
        "publish_action",
        run_id=run_id,
        kind=CheckpointKind.ACTION,
        output=effective_outputs["publish_action"],
        dependencies=("orchestrator",),
        dependency_checkpoints=checkpoints,
        source_class="bounded_demo_side_effect",
        source_ref="demo-side-effect://publish",
        side_effect_key=f"{run_id}:publish",
        policy_version=policy_version,
    )
    return tuple(checkpoints.values())