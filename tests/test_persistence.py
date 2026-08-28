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
    snapshot["checkpoints"].append(
        {
            "checkpoint_id": "policy_rules",
            "kind": "POLICY",
            "dependencies": [],
            "input_digests": [],
            "evidence_digests": [],
            "tool_result_digests": [],
            "output_digest": "digest-policy-v0",
            "integrity_digest": "digest-policy-v0",
            "status": "VERIFIED",
            "policy_version": "policy-v0",
        }
    )

    receipt = persistence.verify_persisted_snapshot(snapshot, action_receipt=None)

    assert receipt.trusted is False
    assert any("policy_rules" in failure and "policy" in failure for failure in receipt.failures)


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


class _FakeDocumentSnapshot:
    def __init__(self, data: dict[str, Any] | None) -> None:
        self._data = copy.deepcopy(data)
        self.exists = data is not None

    def to_dict(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._data)


class _FakeDocumentReference:
    def __init__(self, storage: dict[str, dict[str, Any]], path: str) -> None:
        self._storage = storage
        self._path = path

    def set(self, data: dict[str, Any]) -> None:
        self._storage[self._path] = copy.deepcopy(data)

    def create(self, data: dict[str, Any]) -> None:
        if self._path in self._storage:
            raise AlreadyExists("already exists")
        self.set(data)

    def get(self) -> _FakeDocumentSnapshot:
        return _FakeDocumentSnapshot(self._storage.get(self._path))

    def collection(self, name: str) -> _FakeCollectionReference:
        return _FakeCollectionReference(self._storage, f"{self._path}/{name}")


class _FakeCollectionReference:
    def __init__(self, storage: dict[str, dict[str, Any]], path: str) -> None:
        self._storage = storage
        self._path = path

    def document(self, name: str) -> _FakeDocumentReference:
        return _FakeDocumentReference(self._storage, f"{self._path}/{name}")


class _FakeFirestoreClient:
    def __init__(self) -> None:
        self.storage: dict[str, dict[str, Any]] = {}

    def collection(self, name: str) -> _FakeCollectionReference:
        return _FakeCollectionReference(self.storage, name)


def _fake_firestore_store() -> Any:
    persistence = _persistence_module()
    store = object.__new__(persistence.FirestoreRunStore)
    store.project_id = "evidencebound-rm-c977c1"
    store._client = _FakeFirestoreClient()
    return store


def test_firestore_store_round_trips_snapshot_and_events() -> None:
    store = _fake_firestore_store()
    snapshot = _verified_snapshot()

    store.save_run_snapshot("run-firestore-1", snapshot)
    loaded = store.load_run_snapshot("run-firestore-1")
    assert loaded is not None
    assert loaded["run_id"] == "run-persist-1"
    assert isinstance(loaded["persisted_at"], datetime)
    assert store.load_run_snapshot("missing") is None

    event = FlightEvent(
        event_id=7,
        run_id="run-firestore-1",
        event_type=EventType.ACTION_BLOCKED,
        checkpoint_id="publish_action",
        message="blocked",
    )
    store.append_event(event)
    event_doc = store._client.storage[
        "recovery_mesh_runs/run-firestore-1/events/000007"
    ]
    assert event_doc["event_type"] == "ACTION_BLOCKED"


def test_firestore_action_receipt_is_exactly_once_and_conflict_fails_closed() -> None:
    store = _fake_firestore_store()
    payload = {"run_id": "run-firestore-1", "safe": True}

    first = store.commit("run-firestore-1:publish", payload, run_id="run-firestore-1")
    duplicate = store.commit("run-firestore-1:publish", payload, run_id="run-firestore-1")

    assert first.duplicate_suppressed is False
    assert duplicate.duplicate_suppressed is True
    assert duplicate.payload_digest == first.payload_digest
    loaded = store.get("run-firestore-1:publish")
    assert loaded is not None
    assert loaded.payload_digest == first.payload_digest

    with pytest.raises(RuntimeError, match="different payload"):
        store.commit(
            "run-firestore-1:publish",
            {"run_id": "run-firestore-1", "safe": False},
            run_id="run-firestore-1",
        )


def test_firestore_get_rejects_malformed_receipt_documents() -> None:
    store = _fake_firestore_store()
    doc_id = store._receipt_document_id("malformed")
    path = f"recovery_mesh_action_receipts/{doc_id}"

    store._client.storage[path] = {"committed_at": datetime.now()}
    assert store.get("malformed") is None

    store._client.storage[path] = {"payload_digest": "digest", "committed_at": "bad"}
    assert store.get("malformed") is None


def test_store_from_environment_selects_memory_and_fails_closed(monkeypatch: Any) -> None:
    persistence = _persistence_module()
    monkeypatch.delenv("RECOVERY_MESH_PERSISTENCE_MODE", raising=False)
    assert persistence.store_from_environment().provider_name == "memory"

    monkeypatch.setenv("RECOVERY_MESH_PERSISTENCE_MODE", "firestore")
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_PROJECT"):
        persistence.store_from_environment()

    monkeypatch.setenv("RECOVERY_MESH_PERSISTENCE_MODE", "unsupported")
    with pytest.raises(RuntimeError, match="unsupported"):
        persistence.store_from_environment()
