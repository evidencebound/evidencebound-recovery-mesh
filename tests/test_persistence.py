from __future__ import annotations

import copy
import importlib.util
from datetime import datetime
from typing import Any

import pytest
from google.api_core.exceptions import AlreadyExists

from recovery_mesh.flight_recorder import EventType, FlightEvent


def _persistence_module() -> Any:
    spec = importlib.util.find_spec("recovery_mesh.persistence")
    assert spec is not None, "recovery_mesh.persistence must exist"
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _verified_snapshot() -> dict[str, Any]:
    return {
        "run_id": "run-persist-1",
        "active_policy_version": "policy-v1",
        "checkpoints": [
            {
                "checkpoint_id": "history_snapshot",
                "kind": "EVIDENCE",
                "dependencies": [],
                "input_digests": [],
                "evidence_digests": [],
                "tool_result_digests": [],
                "output_digest": "digest-history",
                "integrity_digest": "digest-history",
                "status": "VERIFIED",
                "policy_version": "policy-v1",
            },
            {
                "checkpoint_id": "statistician",
                "kind": "AGENT",
                "dependencies": ["history_snapshot"],
                "input_digests": ["digest-history"],
                "evidence_digests": ["digest-history"],
                "tool_result_digests": [],
                "output_digest": "digest-stat",
                "integrity_digest": "digest-stat",
                "status": "VERIFIED",
                "policy_version": "policy-v1",
            },
        ],
    }


def test_inmemory_store_round_trips_snapshot() -> None:
    persistence = _persistence_module()
    store = persistence.InMemoryRunStore()
    snapshot = _verified_snapshot()

    store.save_run_snapshot("run-persist-1", snapshot)

    loaded = store.load_run_snapshot("run-persist-1")
    assert loaded == snapshot
    assert loaded is not snapshot
    assert store.load_run_snapshot("missing") is None


def test_rehydration_accepts_bound_verified_snapshot() -> None:
    persistence = _persistence_module()

    receipt = persistence.verify_persisted_snapshot(_verified_snapshot(), action_receipt=None)

    assert receipt.trusted is True
    assert receipt.checked_checkpoints == 2
    assert receipt.failures == ()
    assert receipt.as_dict()["trusted"] is True


def test_rehydration_fails_closed_when_parent_digest_drifted() -> None:
    persistence = _persistence_module()
    snapshot = _verified_snapshot()
    snapshot["checkpoints"][0]["output_digest"] = "changed-history"
    snapshot["checkpoints"][0]["integrity_digest"] = "changed-history"

    receipt = persistence.verify_persisted_snapshot(snapshot, action_receipt=None)

    assert receipt.trusted is False
    assert any(
        "statistician" in failure and "input digest" in failure
        for failure in receipt.failures
    )


def test_rehydration_fails_closed_on_policy_mismatch() -> None:
    persistence = _persistence_module()
    snapshot = _verified_snapshot()
    snapshot["checkpoints"][1]["policy_version"] = "policy-v0"

    receipt = persistence.verify_persisted_snapshot(snapshot, action_receipt=None)

    assert receipt.trusted is False
    assert any("policy" in failure for failure in receipt.failures)


def test_rehydration_rejects_malformed_and_missing_dependencies() -> None:
    persistence = _persistence_module()
    assert persistence.verify_persisted_snapshot({}, None).trusted is False

    snapshot = _verified_snapshot()
    snapshot["checkpoints"].append("bad")
    snapshot["checkpoints"][1]["dependencies"] = ["missing-parent"]
    snapshot["checkpoints"][0]["status"] = "UNKNOWN"
    snapshot["checkpoints"][0]["integrity_digest"] = "different"

    receipt = persistence.verify_persisted_snapshot(snapshot, None)
    assert receipt.trusted is False
    assert any("malformed checkpoint" in failure for failure in receipt.failures)
    assert any("missing dependencies" in failure for failure in receipt.failures)
    assert any("invalid trust state" in failure for failure in receipt.failures)
    assert any("integrity digest mismatch" in failure for failure in receipt.failures)


def test_inmemory_action_receipt_is_idempotent_and_rejects_conflicts() -> None:
    persistence = _persistence_module()
    store = persistence.InMemoryRunStore()
    payload = {"run_id": "run-persist-1", "safe": True}

    first = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")
    duplicate = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")

    assert first.duplicate_suppressed is False
    assert duplicate.duplicate_suppressed is True
    assert duplicate.payload_digest == first.payload_digest
    assert store.get("publish:run-persist-1") == first
    assert store.get("missing") is None

    with pytest.raises(RuntimeError, match="different payload"):
        store.commit(
            "publish:run-persist-1",
            {"run_id": "run-persist-1", "safe": False},
            run_id="run-persist-1",
        )


class _FakeSnapshot:
    def __init__(self, data: dict[str, Any] | None) -> None:
        self._data = copy.deepcopy(data)
        self.exists = data is not None

    def to_dict(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._data)


class _FakeDoc:
    def __init__(self, client: _FakeClient, path: str) -> None:
        self.client = client
        self.path = path

    def set(self, data: dict[str, Any]) -> None:
        self.client.documents[self.path] = copy.deepcopy(data)

    def create(self, data: dict[str, Any]) -> None:
        if self.path in self.client.documents:
            raise AlreadyExists("exists")
        self.set(data)

    def get(self) -> _FakeSnapshot:
        return _FakeSnapshot(self.client.documents.get(self.path))

    def collection(self, name: str) -> _FakeCollection:
        return _FakeCollection(self.client, f"{self.path}/{name}")


class _FakeCollection:
    def __init__(self, client: _FakeClient, path: str) -> None:
        self.client = client
        self.path = path

    def document(self, document_id: str) -> _FakeDoc:
        return _FakeDoc(self.client, f"{self.path}/{document_id}")


class _FakeClient:
    def __init__(self) -> None:
        self.documents: dict[str, dict[str, Any]] = {}

    def collection(self, name: str) -> _FakeCollection:
        return _FakeCollection(self, name)


def test_firestore_store_round_trip_events_and_idempotent_receipts(monkeypatch: Any) -> None:
    persistence = _persistence_module()
    fake = _FakeClient()
    import google.cloud.firestore

    monkeypatch.setattr(google.cloud.firestore, "Client", lambda project: fake)
    store = persistence.FirestoreRunStore("project-1")
    snapshot = _verified_snapshot()

    store.save_run_snapshot("run-persist-1", snapshot)
    loaded = store.load_run_snapshot("run-persist-1")
    assert loaded is not None
    assert loaded["run_id"] == "run-persist-1"
    assert isinstance(loaded["persisted_at"], datetime)
    assert store.load_run_snapshot("missing") is None

    event = FlightEvent(
        event_id=1,
        run_id="run-persist-1",
        event_type=EventType.TRUST_BREAK_DETECTED,
        message="break",
    )
    store.append_event(event)
    assert "recovery_mesh_runs/run-persist-1/events/000001" in fake.documents

    payload = {"run_id": "run-persist-1", "safe": True}
    first = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")
    duplicate = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")
    assert first.duplicate_suppressed is False
    assert duplicate.duplicate_suppressed is True
    assert duplicate.committed_at == first.committed_at

    fetched = store.get("publish:run-persist-1")
    assert fetched is not None
    assert fetched.payload_digest == first.payload_digest
    assert store.get("missing") is None

    with pytest.raises(RuntimeError, match="different payload"):
        store.commit(
            "publish:run-persist-1",
            {"run_id": "run-persist-1", "safe": False},
            run_id="run-persist-1",
        )


def test_store_from_environment_is_explicit_and_fail_closed(monkeypatch: Any) -> None:
    persistence = _persistence_module()
    monkeypatch.delenv("RECOVERY_MESH_PERSISTENCE_MODE", raising=False)
    assert persistence.store_from_environment().provider_name == "memory"

    monkeypatch.setenv("RECOVERY_MESH_PERSISTENCE_MODE", "firestore")
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_PROJECT"):
        persistence.store_from_environment()

    sentinel = object()
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project-1")
    monkeypatch.setattr(persistence, "FirestoreRunStore", lambda project_id: sentinel)
    assert persistence.store_from_environment() is sentinel

    monkeypatch.setenv("RECOVERY_MESH_PERSISTENCE_MODE", "unknown")
    with pytest.raises(RuntimeError, match="unsupported"):
        persistence.store_from_environment()


def test_rehydration_requires_action_receipt_after_completed_recovery() -> None:
    persistence = _persistence_module()
    snapshot = _verified_snapshot()
    snapshot["checkpoints"].append(
        {
            "checkpoint_id": "publish_action",
            "kind": "ACTION",
            "dependencies": ["statistician"],
            "input_digests": ["digest-stat"],
            "evidence_digests": [],
            "tool_result_digests": [],
            "output_digest": "digest-action",
            "integrity_digest": "digest-action",
            "status": "VERIFIED",
            "policy_version": "policy-v1",
        }
    )
    snapshot["events"] = [{"event_type": "RECOVERY_COMPLETED"}]

    missing = persistence.verify_persisted_snapshot(snapshot, None)
    assert missing.trusted is False
    assert any("missing durable action receipt" in failure for failure in missing.failures)
