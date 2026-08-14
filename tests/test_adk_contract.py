from __future__ import annotations

import importlib.util

import pytest

from recovery_mesh.verification import WorkerOutput


def test_adk_app_constructs_when_dependency_is_available() -> None:
    if importlib.util.find_spec("google.adk") is None:
        pytest.skip("google-adk is unavailable in this offline execution environment")
    from app.agent import app, build_execution_agent, root_agent

    assert app.name == "app"
    assert root_agent.name == "recovery_mesh_orchestrator"
    assert {agent.name for agent in root_agent.sub_agents} == {"statistician", "scout", "skeptic"}

    expected_schema = WorkerOutput.model_json_schema()
    for agent_id in ("statistician", "scout", "skeptic", "orchestrator"):
        agent = build_execution_agent(agent_id)
        config = agent.generate_content_config
        assert config is not None
        assert config.temperature == 0.0
        assert config.max_output_tokens == 256
        assert agent.output_schema is None
        assert config.response_mime_type == "application/json"
        assert config.response_json_schema == expected_schema
        assert config.response_json_schema["required"] == ["claim", "evidence_ids", "confidence"]
        assert config.response_json_schema["additionalProperties"] is False

    root_config = root_agent.generate_content_config
    assert root_config is not None
    assert root_config.response_mime_type is None
    assert root_config.response_json_schema is None
