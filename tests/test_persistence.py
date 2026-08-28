from __future__ import annotations

import importlib.util
from typing import Any

import pytest


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


def test_rehydration_accepts_bound_verified_snapshot() -> None:
    persistence = _persistence_module()

    receipt = persistence.verify_persisted_snapshot(_verified_snapshot(), action_receipt=None)

    assert receipt.trusted is True
    assert receipt.checked_checkpoints == 2
    assert receipt.failures == ()


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


def test_inmemory_action_receipt_is_idempotent_and_rejects_conflicts() -> None:
    persistence = _persistence_module()
    store = persistence.InMemoryRunStore()
    payload = {"run_id": "run-persist-1", "safe": True}

    first = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")
    duplicate = store.commit("publish:run-persist-1", payload, run_id="run-persist-1")

    assert first.duplicate_suppressed is False
    assert duplicate.duplicate_suppressed is True
    assert duplicate.payload_digest == first.payload_digest

    with pytest.raises(RuntimeError, match="different payload"):
        store.commit(
            "publish:run-persist-1",
            {"run_id": "run-persist-1", "safe": False},
            run_id="run-persist-1",
        )
