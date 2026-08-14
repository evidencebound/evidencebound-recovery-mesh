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

MODEL = os.getenv("RECOVERY_MESH_MODEL", "gemini-3.5-flash")


def _model(model_name: str) -> Gemini:
    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    )


def build_execution_agent(agent_id: str, *, model_name: str = MODEL) -> Agent:
    """Build a fresh standalone ADK agent for one deterministic DAG checkpoint."""
    instructions = {
        "statistician": """
You are the Statistician in a bounded research fleet. Analyze only the evidence supplied in
this run. Return one compact JSON object with keys claim, evidence_ids, and confidence. Cite
only identifiers present in the prompt, make uncertainty explicit, and never invent missing
observations. Your output is advisory and cannot authorize an action or change Recovery Mesh
trust state.
""".strip(),
        "scout": """
You are the Scout. Extract relevant context only from the supplied controlled fixture and
explicit inputs. Return one compact JSON object with keys claim, evidence_ids, and confidence.
Distinguish observed from missing data and never fill missing fields with guesses. Your output
is advisory and cannot authorize an action or change Recovery Mesh trust state.
""".strip(),
        "skeptic": """
You are the Skeptic. Inspect the supplied peer outputs and evidence references. Return one
compact JSON object with keys claim, evidence_ids, and confidence. Identify unsupported,
contradictory, stale, or overconfident claims. Prefer uncertainty over invented support. You
cannot override deterministic verification.
""".strip(),
        "orchestrator": """
You are the Orchestrator. Synthesize only the supplied specialist outputs and policy. Return
one compact JSON object with keys claim, evidence_ids, and confidence. Never claim that an
output is VERIFIED, safe to publish, or recovered: those states are owned exclusively by the
deterministic EvidenceBound Recovery Mesh runtime after digest, provenance, policy,
dependency, and side-effect checks.
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
    )


def build_root_agent(*, model_name: str = MODEL) -> Agent:
    """ADK multi-agent catalog representation used for framework/deployment inspection."""
    statistician = build_execution_agent("statistician", model_name=model_name)
    scout = build_execution_agent("scout", model_name=model_name)
    skeptic = build_execution_agent("skeptic", model_name=model_name)
    return Agent(
        name="recovery_mesh_orchestrator",
        model=_model(model_name),
        description="Coordinates specialist research while deterministic Recovery Mesh gates trust.",
        instruction="""
Coordinate the specialist research fleet. Delegate quantitative work to statistician, context
work to scout, and adversarial review to skeptic. Never claim VERIFIED, safe-to-publish, or
recovered state. Deterministic EvidenceBound contracts own those decisions.
""".strip(),
        sub_agents=[statistician, scout, skeptic],
    )


root_agent = build_root_agent()
app = App(root_agent=root_agent, name="app")
