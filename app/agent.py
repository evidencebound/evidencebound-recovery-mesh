"""Google ADK fleet definition.

Gemini performs bounded specialist reasoning. EvidenceBound Recovery Mesh owns trust state,
dependency invalidation, action gates, and recovery decisions outside the model.
"""
from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from recovery_mesh.verification import WorkerOutput
from recovery_mesh.workload import AGENT_DEPENDENCIES

MODEL = os.getenv("RECOVERY_MESH_MODEL", "gemini-3.5-flash")


def _model(model_name: str) -> Gemini:
    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    )


def _worker_output_schema(agent_id: str) -> dict[str, Any]:
    """Constrain citations to the deterministic dependency graph for one checkpoint."""
    try:
        allowed = AGENT_DEPENDENCIES[agent_id]
    except KeyError as exc:
        raise ValueError(f"unsupported execution agent: {agent_id}") from exc
    schema = deepcopy(WorkerOutput.model_json_schema())
    evidence_ids = schema["properties"]["evidence_ids"]
    evidence_ids["items"] = {"type": "string", "enum": list(allowed)}
    evidence_ids["minItems"] = 1
    evidence_ids["uniqueItems"] = True
    return schema


def _generation_config(*, agent_id: str | None = None) -> types.GenerateContentConfig:
    """Keep judge-agent output compact, schema-bound, and cost bounded per invocation."""
    if agent_id is not None:
        # Gemini 3.5 Flash thinks by default. Minimal thinking preserves enough visible-output
        # budget for the compact JSON response while deterministic Recovery Mesh owns all trust
        # decisions after generation.
        return types.GenerateContentConfig(
            max_output_tokens=256,
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
            response_mime_type="application/json",
            response_json_schema=_worker_output_schema(agent_id),
        )
    return types.GenerateContentConfig(max_output_tokens=256)


def build_execution_agent(agent_id: str, *, model_name: str = MODEL) -> Agent:
    """Build a fresh standalone ADK agent for one deterministic DAG checkpoint."""
    instructions = {
        "statistician": """
You are the Statistician in a bounded research fleet. Analyze only the evidence supplied in
this run. Return only the configured structured worker response. For evidence_ids, cite only
the dependency checkpoint IDs explicitly listed by the runtime, never nested source IDs or
field values. Make uncertainty explicit and never invent missing observations. Your output is
advisory and cannot authorize an action or change Recovery Mesh trust state.
""".strip(),
        "scout": """
You are the Scout. Extract relevant context only from the supplied controlled fixture and
explicit inputs. Return only the configured structured worker response. For evidence_ids, cite
only the dependency checkpoint IDs explicitly listed by the runtime, never nested source IDs
or field values. Distinguish observed from missing data and never fill missing fields with
guesses. Your output is advisory and cannot authorize an action or change Recovery Mesh trust
state.
""".strip(),
        "skeptic": """
You are the Skeptic. Inspect the supplied peer outputs and evidence references. Return only
the configured structured worker response. For evidence_ids, cite only the dependency
checkpoint IDs explicitly listed by the runtime. Identify unsupported, contradictory, stale,
or overconfident claims. Prefer uncertainty over invented support. You cannot override
deterministic verification.
""".strip(),
        "orchestrator": """
You are the Orchestrator. Synthesize only the supplied specialist outputs and policy. Return
only the configured structured worker response. For evidence_ids, cite only the dependency
checkpoint IDs explicitly listed by the runtime. Never claim that an output is VERIFIED, safe
to publish, or recovered: those states are owned exclusively by the deterministic EvidenceBound
Recovery Mesh runtime after digest, provenance, policy, dependency, and side-effect checks.
""".strip(),
    }
    descriptions = {
        "statistician": "Quantifies only what supplied evidence supports.",
        "scout": "Extracts bounded contextual signals from supplied fixture context.",
        "skeptic": "Challenges unsupported or contradictory claims from peer agents.",
        "orchestrator": "Synthesizes verified dependencies without controlling trust state.",
    }
    try:
        instruction = instructions[agent_id]
    except KeyError as exc:
        raise ValueError(f"unsupported execution agent: {agent_id}") from exc
    return Agent(
        name=agent_id,
        model=_model(model_name),
        description=descriptions[agent_id],
        instruction=instruction,
        generate_content_config=_generation_config(agent_id=agent_id),
    )


def build_root_agent(*, model_name: str = MODEL) -> Agent:
    """ADK multi-agent catalog representation used for framework/deployment inspection."""
    statistician = build_execution_agent("statistician", model_name=model_name)
    scout = build_execution_agent("scout", model_name=model_name)
    skeptic = build_execution_agent("skeptic", model_name=model_name)
    return Agent(
        name="recovery_mesh_orchestrator",
        model=_model(model_name),
        description=(
            "Coordinates specialist research while deterministic Recovery Mesh gates trust."
        ),
        instruction="""
Coordinate the specialist research fleet. Delegate quantitative work to statistician, context
work to scout, and adversarial review to skeptic. Never claim VERIFIED, safe-to-publish, or
recovered state. Deterministic EvidenceBound contracts own those decisions.
""".strip(),
        generate_content_config=_generation_config(),
        sub_agents=[statistician, scout, skeptic],
    )


root_agent = build_root_agent()
app = App(root_agent=root_agent, name="app")
