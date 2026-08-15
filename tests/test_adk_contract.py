from __future__ import annotations

import importlib.util

import pytest

from recovery_mesh.workload import AGENT_DEPENDENCIES


def test_adk_app_constructs_when_dependency_is_available() -> None:
    if importlib.util.find_spec("google.adk") is None:
        pytest.skip("google-adk is unavailable in this offline execution environment")
    from google.genai import types

    from app.agent import app, build_execution_agent, root_agent

    assert app.name == "app"
    assert root_agent.name == "recovery_mesh_orchestrator"
    assert {agent.name for agent in root_agent.sub_agents} == {"statistician", "scout", "skeptic"}

    for agent_id in ("statistician", "scout", "skeptic", "orchestrator"):
        agent = build_execution_agent(agent_id)
        config = agent.generate_content_config
        assert config is not None
        assert config.temperature is None
        assert config.max_output_tokens == 256
        assert config.thinking_config is not None
        assert config.thinking_config.thinking_level == types.ThinkingLevel.MINIMAL
        assert agent.output_schema is None
        assert config.response_mime_type == "application/json"
        assert config.response_json_schema is not None
        assert config.response_json_schema["required"] == ["claim", "evidence_ids", "confidence"]
        assert config.response_json_schema["additionalProperties"] is False
        evidence_schema = config.response_json_schema["properties"]["evidence_ids"]
        assert evidence_schema["items"]["enum"] == list(AGENT_DEPENDENCIES[agent_id])
        assert evidence_schema["minItems"] == 1
        assert evidence_schema["uniqueItems"] is True

    root_config = root_agent.generate_content_config
    assert root_config is not None
    assert root_config.temperature is None
    assert root_config.response_mime_type is None
    assert root_config.response_json_schema is None
    assert root_config.thinking_config is None
