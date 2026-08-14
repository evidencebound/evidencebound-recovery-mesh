from __future__ import annotations

import asyncio
import json
import os
from time import perf_counter_ns
from typing import Any

from .execution import AgentExecutionError, AgentExecutionReceipt, ExecutionUnavailable


class GoogleAdkExecutor:
    """Live Gemini executor using Google ADK with imports deferred until invocation."""

    provider_name = "google_adk_vertex"
    is_live_google = True

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name: str | None = model_name or os.getenv(
            "RECOVERY_MESH_MODEL", "gemini-3.5-flash"
        )

    def execute(
        self,
        *,
        run_id: str,
        checkpoint_id: str,
        prompt: str,
    ) -> AgentExecutionReceipt:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(
                self._execute_async(
                    run_id=run_id,
                    checkpoint_id=checkpoint_id,
                    prompt=prompt,
                )
            )
        raise ExecutionUnavailable(
            "GoogleAdkExecutor sync entrypoint cannot run inside an active event loop"
        )

    async def _execute_async(
        self,
        *,
        run_id: str,
        checkpoint_id: str,
        prompt: str,
    ) -> AgentExecutionReceipt:
        try:
            from google.adk.runners import InMemoryRunner
            from google.genai import types

            from app.agent import build_execution_agent
        except ImportError as exc:
            raise ExecutionUnavailable(
                "google-adk/google-genai is unavailable; live Google execution cannot start"
            ) from exc

        agent = build_execution_agent(
            checkpoint_id, model_name=self.model_name or "gemini-3.5-flash"
        )
        app_name = f"recovery_mesh_{checkpoint_id}"
        runner = InMemoryRunner(agent=agent, app_name=app_name)
        start = perf_counter_ns()
        try:
            session = await runner.session_service.create_session(
                app_name=app_name,
                user_id=f"mesh-{run_id}",
            )
            message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
            events: list[Any] = []
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=message,
            ):
                events.append(event)
        except Exception as exc:
            raise AgentExecutionError(
                f"ADK execution failed for {checkpoint_id}: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            close = getattr(runner, "close", None)
            if close is not None:
                maybe_awaitable = close()
                if hasattr(maybe_awaitable, "__await__"):
                    await maybe_awaitable

        elapsed_us = max(1, (perf_counter_ns() - start) // 1_000)
        text = _last_final_text(events, expected_author=agent.name)
        if not text:
            raise AgentExecutionError(f"ADK execution for {checkpoint_id} returned no final text")

        structured_output = _parse_agent_output(text)
        usage = _usage_totals(events)
        invocation_ids = tuple(
            dict.fromkeys(
                value
                for event in events
                if (value := getattr(event, "invocation_id", None))
            )
        )
        event_authors = tuple(
            dict.fromkeys(
                value for event in events if (value := getattr(event, "author", None))
            )
        )
        return AgentExecutionReceipt(
            checkpoint_id=checkpoint_id,
            agent_id=agent.name,
            provider=self.provider_name,
            model=self.model_name,
            structured_output=structured_output,
            elapsed_us=elapsed_us,
            model_calls=usage["model_calls"],
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            total_tokens=usage["total_tokens"],
            invocation_ids=invocation_ids,
            event_authors=event_authors,
        )


def _last_final_text(events: list[Any], *, expected_author: str) -> str | None:
    candidates: list[str] = []
    for event in events:
        if getattr(event, "partial", False):
            continue
        author = getattr(event, "author", None)
        if author not in {expected_author, "recovery_mesh_orchestrator"}:
            continue
        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) if content is not None else None
        if not parts:
            continue
        text = "".join(str(part.text) for part in parts if getattr(part, "text", None))
        if text.strip():
            candidates.append(text.strip())
    return candidates[-1] if candidates else None


def _parse_agent_output(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return {"raw_text": text, "format": "text"}
    if isinstance(parsed, dict):
        return parsed
    return {"value": parsed, "format": "json_non_object"}


def _usage_totals(events: list[Any]) -> dict[str, int | None]:
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    model_calls = 0
    saw_input = False
    saw_output = False
    saw_total = False

    for event in events:
        usage = getattr(event, "usage_metadata", None)
        if usage is None:
            continue
        model_calls += 1
        prompt = getattr(usage, "prompt_token_count", None)
        candidates = getattr(usage, "candidates_token_count", None)
        total = getattr(usage, "total_token_count", None)
        if isinstance(prompt, int):
            input_tokens += prompt
            saw_input = True
        if isinstance(candidates, int):
            output_tokens += candidates
            saw_output = True
        if isinstance(total, int):
            total_tokens += total
            saw_total = True

    return {
        "model_calls": model_calls or None,
        "input_tokens": input_tokens if saw_input else None,
        "output_tokens": output_tokens if saw_output else None,
        "total_tokens": total_tokens if saw_total else None,
    }
