"""Google ADK fleet definition.

Gemini performs bounded specialist reasoning. EvidenceBound Recovery Mesh owns trust state,
dependency invalidation, action gates, and recovery decisions outside the model.
"""
from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from recovery_mesh.verification import WorkerOutput

MODEL = os.getenv("RECOVERY_MESH_MODEL", "gemini-3.5-flash")


def _model(model_name: str) -> Gemini:
    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    )


def _generation_config(*, structured_worker_output: bool) -> types.GenerateContentConfig:
    """Keep judge-agent output compact, deterministic, and cost bounded per invocation."""
    if structured_worker_output:
        # ADK 2.7.0 currently yields an empty final Event for this workload when
        # LlmAgent.output_schema is used directly. Keep the agent execution in ADK,
        # but use Gemini's native JSON-schema generation contract so the final event
        # carries normal model text. Recovery Mesh independently validates the same
        # WorkerOutput schema again after generation.
        return types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=256,
            response_mime_type="application/json",
            response_json_schema=WorkerOutput.model_json_schema(),
        )
    return types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=256,
    )


def build_execution_agent(agent_id: str, *, model_name: str = MODEL) -> Agent:
    """Build a fresh standalone ADK agent for one deterministic DAG checkpoint."""
    instructions = {
        "statistician": """
You are the Statistician in a bounded research fleet. Analyze only the evidence supplied in
this run. Return only the configured structured worker response. Cite only identifiers present
in the prompt, make uncertainty explicit, and never invent missing observations. Your output
is advisory and cannot authorize an action or change Recovery Mesh trust state.
""".strip(),
        "scout": """
You are the Scout. Extract relevant context only from the supplied controlled fixture and
explicit inputs. Return only the configured structured worker response. Distinguish observed
from missing data and never fill missing fields with guesses. Your output is advisory and
cannot authorize an action or change Recovery Mesh trust state.
""".strip(),
        "skeptic": """
You are the Skeptic. Inspect the supplied peer outputs and evidence references. Return only
the configured structured worker response. Identify unsupported, contradictory, stale, or
overconfident claims. Prefer uncertainty over invented support. You cannot override
deterministic verification.
""".strip(),
        "orchestrator": """
You are the Orchestrator. Synthesize only the supplied specialist outputs and policy. Return
only the configured structured worker response. Never claim that an output is VERIFIED, safe
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
        generate_content_config=_generation_config(structured_worker_output=True),
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
        generate_content_config=_generation_config(structured_worker_output=False),
        sub_agents=[statistician, scout, skeptic],
    )


root_agent = build_root_agent()
app = App(root_agent=root_agent, name="app")
