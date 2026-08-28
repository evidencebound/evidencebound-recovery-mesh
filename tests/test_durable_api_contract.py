from __future__ import annotations

from fastapi.testclient import TestClient

import recovery_mesh.api as api


def test_health_exposes_persistence_metadata() -> None:
    response = TestClient(api.app).get("/health")
    assert response.status_code == 200
    persistence = response.json()["persistence"]
    assert persistence["provider"] in {"memory", "firestore"}
    assert isinstance(persistence["durable"], bool)


def test_durable_readback_tracks_blocked_then_verified_action() -> None:
    client = TestClient(api.app)
    api._runs.clear()

    created = client.post("/api/runs")
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    baseline = client.get(f"/api/durable-runs/{run_id}")
    assert baseline.status_code == 200
    assert baseline.json()["rehydration"]["trusted"] is True
    assert baseline.json()["action_receipt"] is None

    faulted = client.post(f"/api/runs/{run_id}/fault/stale_evidence")
    assert faulted.status_code == 200
    checkpoints = {item["checkpoint_id"]: item for item in faulted.json()["checkpoints"]}
    assert checkpoints["publish_action"]["status"] == "BLOCKED"

    blocked = client.get(f"/api/durable-runs/{run_id}")
    assert blocked.status_code == 200
    assert blocked.json()["action_receipt"] is None
    assert blocked.json()["rehydration"]["trusted"] is True

    recovered = client.post(f"/api/runs/{run_id}/recover")
    assert recovered.status_code == 200
    assert recovered.json()["persistence"]["action_receipt_committed"] is True

    durable = client.get(f"/api/durable-runs/{run_id}")
    assert durable.status_code == 200
    assert durable.json()["rehydration"]["trusted"] is True
    assert durable.json()["action_receipt"] is not None


def test_durable_readback_missing_run_is_404() -> None:
    response = TestClient(api.app).get("/api/durable-runs/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "durable run not found"
