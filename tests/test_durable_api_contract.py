from __future__ import annotations

from fastapi.testclient import TestClient

from recovery_mesh.api import app


def test_health_exposes_persistence_metadata() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    persistence = response.json()["persistence"]
    assert persistence["provider"] in {"memory", "firestore"}
    assert isinstance(persistence["durable"], bool)
