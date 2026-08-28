from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from threading import Lock
from typing import Any, Protocol

from .flight_recorder import FlightEvent
from .hashing import sha256_digest
from .recovery import SideEffectReceipt


@dataclass(frozen=True)
class RehydrationReceipt:
    trusted: bool
    checked_checkpoints: int
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "trusted": self.trusted,
            "checked_checkpoints": self.checked_checkpoints,
            "failures": list(self.failures),
        }


class RunStore(Protocol):
    provider_name: str
    durable: bool
    project_id: str | None

    def save_run_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> None: ...

    def load_run_snapshot(self, run_id: str) -> dict[str, Any] | None: ...

    def append_event(self, event: FlightEvent) -> None: ...

    def commit(self, key: str, payload: Any, *, run_id: str | None = None) -> SideEffectReceipt: ...

    def get(self, key: str) -> SideEffectReceipt | None: ...


class InMemoryRunStore:
    provider_name = "memory"
    durable = False
    project_id: str | None = None

    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._events: dict[str, dict[int, dict[str, Any]]] = {}
        self._receipts: dict[str, SideEffectReceipt] = {}
        self._lock = Lock()

    def save_run_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> None:
        with self._lock:
            self._snapshots[run_id] = copy.deepcopy(snapshot)

    def load_run_snapshot(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            snapshot = self._snapshots.get(run_id)
            return copy.deepcopy(snapshot) if snapshot is not None else None

    def append_event(self, event: FlightEvent) -> None:
        with self._lock:
            self._events.setdefault(event.run_id, {})[event.event_id] = event.model_dump(
                mode="json"
            )

    def commit(
        self,
        key: str,
        payload: Any,
        *,
        run_id: str | None = None,
    ) -> SideEffectReceipt:
        del run_id
        payload_digest = sha256_digest(payload)
        with self._lock:
            existing = self._receipts.get(key)
            if existing is not None:
                if existing.payload_digest != payload_digest:
                    raise RuntimeError("idempotency key reused with different payload")
                return SideEffectReceipt(
                    side_effect_key=key,
                    payload_digest=payload_digest,
                    committed_at=existing.committed_at,
                    duplicate_suppressed=True,
                )
            receipt = SideEffectReceipt(
                side_effect_key=key,
                payload_digest=payload_digest,
                committed_at=datetime.now(UTC),
                duplicate_suppressed=False,
            )
            self._receipts[key] = receipt
            return receipt

    def get(self, key: str) -> SideEffectReceipt | None:
        with self._lock:
            return self._receipts.get(key)


class FirestoreRunStore:
    provider_name = "firestore"
    durable = True
    project_id: str | None

    def __init__(self, project_id: str) -> None:
        from google.cloud import firestore

        self.project_id = project_id
        self._client = firestore.Client(project=project_id)

    @staticmethod
    def _receipt_document_id(key: str) -> str:
        return sha256(key.encode("utf-8")).hexdigest()

    def save_run_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> None:
        document = copy.deepcopy(snapshot)
        document["persisted_at"] = datetime.now(UTC)
        self._client.collection("recovery_mesh_runs").document(run_id).set(document)

    def load_run_snapshot(self, run_id: str) -> dict[str, Any] | None:
        result = self._client.collection("recovery_mesh_runs").document(run_id).get()
        if not result.exists:
            return None
        data = result.to_dict()
        return dict(data) if data is not None else None

    def append_event(self, event: FlightEvent) -> None:
        self._client.collection("recovery_mesh_runs").document(event.run_id).collection(
            "events"
        ).document(f"{event.event_id:06d}").set(event.model_dump(mode="json"))

    def commit(
        self,
        key: str,
        payload: Any,
        *,
        run_id: str | None = None,
    ) -> SideEffectReceipt:
        from google.api_core.exceptions import AlreadyExists

        payload_digest = sha256_digest(payload)
        committed_at = datetime.now(UTC)
        ref = self._client.collection("recovery_mesh_action_receipts").document(
            self._receipt_document_id(key)
        )
        document = {
            "side_effect_key": key,
            "payload_digest": payload_digest,
            "run_id": run_id,
            "committed_at": committed_at,
        }
        try:
            ref.create(document)
        except AlreadyExists:
            existing = ref.get().to_dict() or {}
            if existing.get("payload_digest") != payload_digest:
                raise RuntimeError("idempotency key reused with different payload") from None
            existing_time = existing.get("committed_at")
            if not isinstance(existing_time, datetime):
                existing_time = committed_at
            return SideEffectReceipt(
                side_effect_key=key,
                payload_digest=payload_digest,
                committed_at=existing_time,
                duplicate_suppressed=True,
            )
        return SideEffectReceipt(
            side_effect_key=key,
            payload_digest=payload_digest,
            committed_at=committed_at,
            duplicate_suppressed=False,
        )

    def get(self, key: str) -> SideEffectReceipt | None:
        ref = self._client.collection("recovery_mesh_action_receipts").document(
            self._receipt_document_id(key)
        )
        result = ref.get()
        if not result.exists:
            return None
        data = result.to_dict() or {}
        payload_digest = data.get("payload_digest")
        if not isinstance(payload_digest, str):
            return None
        committed_at = data.get("committed_at")
        if not isinstance(committed_at, datetime):
            return None
        return SideEffectReceipt(
            side_effect_key=key,
            payload_digest=payload_digest,
            committed_at=committed_at,
            duplicate_suppressed=False,
        )


def store_from_environment() -> RunStore:
    mode = os.getenv("RECOVERY_MESH_PERSISTENCE_MODE", "memory").strip().lower()
    if mode in {"", "memory", "inmemory"}:
        return InMemoryRunStore()
    if mode == "firestore":
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
        if not project_id:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is required for Firestore persistence")
        return FirestoreRunStore(project_id)
    raise RuntimeError(f"unsupported RECOVERY_MESH_PERSISTENCE_MODE: {mode}")


def _policy_bound_checkpoint_ids(
    checkpoints: dict[str, dict[str, Any]],
) -> set[str]:
    policy_bound = {
        checkpoint_id
        for checkpoint_id, item in checkpoints.items()
        if item.get("kind") == "POLICY"
    }
    for _ in range(len(checkpoints)):
        before = len(policy_bound)
        for checkpoint_id, item in checkpoints.items():
            dependencies = item.get("dependencies", [])
            if not isinstance(dependencies, list):
                continue
            if any(dependency in policy_bound for dependency in dependencies):
                policy_bound.add(checkpoint_id)
        if len(policy_bound) == before:
            break
    return policy_bound


def verify_persisted_snapshot(
    snapshot: dict[str, Any],
    action_receipt: SideEffectReceipt | None,
) -> RehydrationReceipt:
    failures: list[str] = []
    checkpoints_raw = snapshot.get("checkpoints")
    if not isinstance(checkpoints_raw, list):
        return RehydrationReceipt(False, 0, ("checkpoints missing",))

    checkpoints: dict[str, dict[str, Any]] = {}
    for item in checkpoints_raw:
        if not isinstance(item, dict):
            failures.append("malformed checkpoint")
            continue
        checkpoint_id = item.get("checkpoint_id")
        if not isinstance(checkpoint_id, str) or checkpoint_id in checkpoints:
            failures.append("invalid or duplicate checkpoint id")
            continue
        checkpoints[checkpoint_id] = item

    active_policy = snapshot.get("active_policy_version")
    policy_bound = _policy_bound_checkpoint_ids(checkpoints)
    allowed_states = {"VERIFIED", "INVALIDATED", "RECOMPUTE", "BLOCKED"}
    for checkpoint_id, item in checkpoints.items():
        status = item.get("status")
        if status not in allowed_states:
            failures.append(f"{checkpoint_id}: invalid trust state")
        output_digest = item.get("output_digest")
        integrity_digest = item.get("integrity_digest")
        if output_digest and integrity_digest and output_digest != integrity_digest:
            failures.append(f"{checkpoint_id}: integrity digest mismatch")
        dependencies = item.get("dependencies", [])
        if not isinstance(dependencies, list):
            failures.append(f"{checkpoint_id}: dependencies malformed")
            continue
        missing = [dep for dep in dependencies if dep not in checkpoints]
        if missing:
            failures.append(f"{checkpoint_id}: missing dependencies {missing}")
            continue
        if status == "VERIFIED":
            if (
                checkpoint_id in policy_bound
                and active_policy is not None
                and item.get("policy_version") != active_policy
            ):
                failures.append(f"{checkpoint_id}: policy version mismatch")
            expected_inputs = [checkpoints[dep].get("output_digest") for dep in dependencies]
            if list(item.get("input_digests", [])) != expected_inputs:
                failures.append(f"{checkpoint_id}: input digest binding mismatch")

    recovery_completed = any(
        isinstance(event, dict) and event.get("event_type") == "RECOVERY_COMPLETED"
        for event in snapshot.get("events", [])
    )
    action = checkpoints.get("publish_action")
    if action is not None and action.get("status") == "BLOCKED" and action_receipt is not None:
        failures.append("publish_action: BLOCKED state has an unexpected durable receipt")
    if recovery_completed and action is not None and action.get("status") == "VERIFIED":
        if action_receipt is None:
            failures.append("publish_action: verified recovery missing durable action receipt")
        else:
            action_receipt_data = snapshot.get("action_receipt")
            if isinstance(action_receipt_data, dict):
                persisted_digest = action_receipt_data.get("payload_digest")
                if persisted_digest and persisted_digest != action_receipt.payload_digest:
                    failures.append("publish_action: durable action receipt digest mismatch")

    return RehydrationReceipt(
        trusted=not failures,
        checked_checkpoints=len(checkpoints),
        failures=tuple(failures),
    )
