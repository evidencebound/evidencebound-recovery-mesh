from __future__ import annotations

from fastapi.testclient import TestClient

from recovery_mesh.api import app

client = TestClient(app)


def test_health_and_judge_api_flow() -> None:
    health = client.get("/healthz").json()
    assert health["status"] == "ok"
    assert health["judge_access_required"] is False
    assert health["judge_key_header"] == "X-Recovery-Mesh-Judge-Key"

    created = client.post("/api/runs").json()
    run_id = created["run_id"]

    faulted = client.post(f"/api/runs/{run_id}/fault/stale_evidence")
    assert faulted.status_code == 200
    assert faulted.json()["active_blast_radius"]["invalidated_source"] == "history_snapshot"

    recovered = client.post(f"/api/runs/{run_id}/recover")
    assert recovered.status_code == 200
    body = recovered.json()
    assert body["active_blast_radius"] is None
    assert body["benchmark"]["measurement_class"] == "deterministic_core_only"


def test_judge_key_protects_action_and_run_endpoints(monkeypatch) -> None:
    monkeypatch.setenv("RECOVERY_MESH_JUDGE_KEY", "judge-secret-for-test")
    headers = {"X-Recovery-Mesh-Judge-Key": "judge-secret-for-test"}

    health = client.get("/healthz").json()
    assert health["judge_access_required"] is True

    assert client.post("/api/runs").status_code == 401
    assert client.post("/api/runs", headers={"X-Recovery-Mesh-Judge-Key": "wrong"}).status_code == 401

    created = client.post("/api/runs", headers=headers)
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    assert client.get(f"/api/runs/{run_id}").status_code == 401
    assert client.get(f"/api/runs/{run_id}", headers=headers).status_code == 200
    assert client.post(f"/api/runs/{run_id}/fault/stale_evidence").status_code == 401
    assert client.post(f"/api/runs/{run_id}/fault/stale_evidence", headers=headers).status_code == 200
    assert client.post(f"/api/runs/{run_id}/recover", headers=headers).status_code == 200


def test_live_mode_without_judge_key_fails_action_gate_closed(monkeypatch) -> None:
    monkeypatch.delenv("RECOVERY_MESH_JUDGE_KEY", raising=False)
    monkeypatch.setenv("RECOVERY_MESH_EXECUTION_MODE", "google_adk")

    response = client.post("/api/runs")
    assert response.status_code == 503
    assert "judge access key is not configured" in response.json()["detail"]


def test_unknown_scenario_fails_closed() -> None:
    run_id = client.post("/api/runs").json()["run_id"]
    response = client.post(f"/api/runs/{run_id}/fault/unknown")
    assert response.status_code == 400


def test_missing_run_and_recover_without_fault_fail_closed() -> None:
    assert client.get("/api/runs/does-not-exist").status_code == 404
    run_id = client.post("/api/runs").json()["run_id"]
    response = client.post(f"/api/runs/{run_id}/recover")
    assert response.status_code == 409
    assert "no active trust break" in response.json()["detail"]


def test_second_fault_is_rejected_until_recovery() -> None:
    run_id = client.post("/api/runs").json()["run_id"]
    assert client.post(f"/api/runs/{run_id}/fault/stale_evidence").status_code == 200
    second = client.post(f"/api/runs/{run_id}/fault/policy_drift")
    assert second.status_code == 409
    assert "already active" in second.json()["detail"]


def test_health_exposes_execution_mode_without_claiming_google() -> None:
    body = client.get("/healthz").json()
    assert body["execution"]["provider"] == "deterministic_test"
    assert body["execution"]["live_google"] is False
