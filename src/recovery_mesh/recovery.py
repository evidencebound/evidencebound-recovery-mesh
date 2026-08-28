from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Protocol

from .graph import TrustGraph
from .hashing import sha256_digest
from .models import (
    Checkpoint,
    CheckpointKind,
    ProvenanceMetadata,
    TrustBreak,
    TrustStatus,
)


class RecoveryInvariantError(RuntimeError):
    pass


@dataclass(frozen=True)
class BlastRadius:
    invalidated_source: str
    contaminated_checkpoints: tuple[str, ...]
    recomputation_set: tuple[str, ...]
    blocked_action_nodes: tuple[str, ...]
    reusable_checkpoints: tuple[str, ...]


@dataclass(frozen=True)
class RecoveryPlan:
    trust_break: TrustBreak
    blast_radius: BlastRadius
    rerun_order: tuple[str, ...]


@dataclass(frozen=True)
class SideEffectReceipt:
    side_effect_key: str
    payload_digest: str
    committed_at: datetime
    duplicate_suppressed: bool


class ActionLedger(Protocol):
    def commit(
        self,
        key: str,
        payload: Any,
        *,
        run_id: str | None = None,
    ) -> SideEffectReceipt: ...


class SideEffectLedger:
    """Thread-safe process-local idempotency ledger for local/test execution."""

    def __init__(self) -> None:
        self._receipts: dict[str, SideEffectReceipt] = {}
        self._lock = Lock()

    def commit(
        self,
        key: str,
        payload: Any,
        *,
        run_id: str | None = None,
    ) -> SideEffectReceipt:
        del run_id
        digest = sha256_digest(payload)
        with self._lock:
            existing = self._receipts.get(key)
            if existing is not None:
                if existing.payload_digest != digest:
                    raise RecoveryInvariantError(
                        "idempotency key already committed with a different payload"
                    )
                return SideEffectReceipt(
                    side_effect_key=key,
                    payload_digest=digest,
                    committed_at=existing.committed_at,
                    duplicate_suppressed=True,
                )
            receipt = SideEffectReceipt(
                side_effect_key=key,
                payload_digest=digest,
                committed_at=datetime.now(UTC),
                duplicate_suppressed=False,
            )
            self._receipts[key] = receipt
            return receipt

    def get(self, key: str) -> SideEffectReceipt | None:
        with self._lock:
            return self._receipts.get(key)


class RecoveryEngine:
    def __init__(self, graph: TrustGraph):
        self.graph = graph

    def plan(self, trust_break: TrustBreak) -> RecoveryPlan:
        if trust_break.run_id != self.graph.run_id:
            raise RecoveryInvariantError("trust break run_id does not match graph")
        source = self.graph.checkpoint(trust_break.checkpoint_id)
        descendants = self.graph.descendants(source.checkpoint_id)

        blocked_actions = {
            checkpoint_id
            for checkpoint_id in descendants | {source.checkpoint_id}
            if self.graph.checkpoint(checkpoint_id).kind is CheckpointKind.ACTION
        }
        recompute = {
            checkpoint_id
            for checkpoint_id in descendants | {source.checkpoint_id}
            if self.graph.checkpoint(checkpoint_id).kind is not CheckpointKind.ACTION
        }
        contaminated = set(descendants)
        affected = {source.checkpoint_id} | contaminated
        reusable = {
            item.checkpoint_id
            for item in self.graph.checkpoints
            if item.checkpoint_id not in affected
            and item.verification_status is TrustStatus.VERIFIED
        }

        blast = BlastRadius(
            invalidated_source=source.checkpoint_id,
            contaminated_checkpoints=self.graph.topological_subset(contaminated),
            recomputation_set=self.graph.topological_subset(recompute),
            blocked_action_nodes=self.graph.topological_subset(blocked_actions),
            reusable_checkpoints=self.graph.topological_subset(reusable),
        )
        return RecoveryPlan(
            trust_break=trust_break,
            blast_radius=blast,
            rerun_order=blast.recomputation_set,
        )

    def apply_plan(self, plan: RecoveryPlan) -> TrustGraph:
        replacements: list[Checkpoint] = []
        source_id = plan.blast_radius.invalidated_source
        for checkpoint_id in plan.blast_radius.recomputation_set:
            item = self.graph.checkpoint(checkpoint_id)
            status = (
                TrustStatus.INVALIDATED
                if checkpoint_id == source_id
                else TrustStatus.RECOMPUTE
            )
            replacements.append(
                item.model_copy(update={"verification_status": status, "verified_at": None})
            )
        for checkpoint_id in plan.blast_radius.blocked_action_nodes:
            item = self.graph.checkpoint(checkpoint_id)
            replacements.append(
                item.model_copy(
                    update={"verification_status": TrustStatus.BLOCKED, "verified_at": None}
                )
            )
        self.graph = self.graph.replace_many(replacements)
        return self.graph

    def verify_recomputed(
        self,
        checkpoint_id: str,
        *,
        structured_output: Any,
        input_digests: tuple[str, ...] | None = None,
        evidence_digests: tuple[str, ...] | None = None,
        tool_result_digests: tuple[str, ...] | None = None,
        policy_version: str | None = None,
        provenance: ProvenanceMetadata | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Checkpoint:
        current = self.graph.checkpoint(checkpoint_id)
        if current.kind is CheckpointKind.ACTION:
            raise RecoveryInvariantError("action nodes are resumed via resume_action")
        if current.verification_status not in {TrustStatus.INVALIDATED, TrustStatus.RECOMPUTE}:
            raise RecoveryInvariantError("checkpoint is not awaiting recomputation")
        for parent_id in current.dependency_checkpoint_ids:
            parent = self.graph.checkpoint(parent_id)
            if parent.verification_status is not TrustStatus.VERIFIED:
                raise RecoveryInvariantError(
                    f"cannot verify {checkpoint_id}; dependency {parent_id} is not VERIFIED"
                )
        digest = sha256_digest(structured_output)
        replacement = current.model_copy(
            update={
                "structured_output_digest": digest,
                "integrity": current.integrity.model_copy(update={"digest": digest}),
                "input_digests": (
                    input_digests if input_digests is not None else current.input_digests
                ),
                "evidence_digests": (
                    evidence_digests if evidence_digests is not None else current.evidence_digests
                ),
                "tool_result_digests": (
                    tool_result_digests
                    if tool_result_digests is not None
                    else current.tool_result_digests
                ),
                "policy_version": policy_version or current.policy_version,
                "provenance": provenance or current.provenance,
                "metadata": metadata if metadata is not None else current.metadata,
                "verification_status": TrustStatus.VERIFIED,
                "verified_at": datetime.now(UTC),
            }
        )
        self.graph = self.graph.replace(replacement)
        return replacement

    def resume_action(
        self,
        checkpoint_id: str,
        *,
        payload: Any,
        ledger: ActionLedger,
    ) -> SideEffectReceipt:
        action = self.graph.checkpoint(checkpoint_id)
        if action.kind is not CheckpointKind.ACTION:
            raise RecoveryInvariantError("resume_action requires an ACTION checkpoint")
        for parent_id in action.dependency_checkpoint_ids:
            parent = self.graph.checkpoint(parent_id)
            if parent.verification_status is not TrustStatus.VERIFIED:
                raise RecoveryInvariantError(
                    f"action remains BLOCKED; dependency {parent_id} is not VERIFIED"
                )
        if not action.side_effect_key:
            raise RecoveryInvariantError("action has no side_effect_key")
        receipt = ledger.commit(action.side_effect_key, payload, run_id=self.graph.run_id)
        digest = sha256_digest(payload)
        replacement = action.model_copy(
            update={
                "structured_output_digest": digest,
                "integrity": action.integrity.model_copy(update={"digest": digest}),
                "input_digests": tuple(
                    self.graph.checkpoint(parent_id).structured_output_digest
                    for parent_id in action.dependency_checkpoint_ids
                ),
                "verification_status": TrustStatus.VERIFIED,
                "verified_at": datetime.now(UTC),
            }
        )
        self.graph = self.graph.replace(replacement)
        return receipt
