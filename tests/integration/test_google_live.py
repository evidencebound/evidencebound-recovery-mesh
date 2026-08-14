from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.getenv("RUN_GOOGLE_INTEGRATION") != "1",
    reason="live Google invocation is opt-in and requires real Vertex AI credentials",
)
def test_live_adk_gemini_invocation() -> None:
    """Actual Gemini/ADK gate; never count a skipped test as PASS."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    from app.agent import root_agent

    runner = InMemoryRunner(agent=root_agent, app_name="recovery-mesh-live-test")
    session = runner.session_service.create_session_sync(
        app_name="recovery-mesh-live-test",
        user_id="integration-test",
    )
    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    "Delegate bounded analysis of this controlled fixture to the specialist fleet. "
                    "Fixture: Northport FC vs Lakeside FC. Evidence: sample_size=18. "
                    "State missing evidence explicitly and do not claim VERIFIED status."
                )
            )
        ],
    )
    events = list(
        runner.run(
            user_id=session.user_id,
            session_id=session.id,
            new_message=message,
        )
    )
    assert events
    authors = {event.author for event in events if getattr(event, "author", None)}
    assert "recovery_mesh_orchestrator" in authors
    # A true multi-agent acceptance run must prove at least one delegated specialist event.
    assert authors.intersection({"statistician", "scout", "skeptic"})
