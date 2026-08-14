from __future__ import annotations

import importlib.util

import pytest


def test_adk_app_constructs_when_dependency_is_available() -> None:
    if importlib.util.find_spec("google.adk") is None:
        pytest.skip("google-adk is unavailable in this offline execution environment")
    from app.agent import app, root_agent

    assert app.name == "app"
    assert root_agent.name == "recovery_mesh_orchestrator"
    assert {agent.name for agent in root_agent.sub_agents} == {"statistician", "scout", "skeptic"}
