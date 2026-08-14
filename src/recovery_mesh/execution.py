from __future__ import annotations

import json
import os
from dataclasses import dataclass
from threading import Lock
from time import perf_counter_ns
from typing import Any, Protocol


class ExecutionUnavailable(RuntimeError):
    """Raised when the configured execution provider cannot be constructed."""


class AgentExecutionError(RuntimeError):
    """Raised when an agent invocation fails or returns no usable output."""


@dataclass(frozen=True)
class AgentExecutionReceipt:
    checkpoint_id: str
    agent_id: str
    provider: str
    model: str | None
    structured_output: dict[str, Any]
    elapsed_us: int
    model_calls: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    invocation_ids: tuple[str, ...] = ()
    event_authors: tuple[str, ...] = ()

    @property
    def source_ref(self) -> str | None:
        if not self.invocation_ids:
            return None
        return f"adk://{self.invocation_ids[-1]}"


class FleetExecutor(Protocol):
    provider_name: str
    model_name: str | None
    is_live_google: bool

    def execute(
        self,
        *,
        run_id: str,
        checkpoint_id: str,
        prompt: str,
    ) -> AgentExecutionReceipt: ...


class ModelCallBudget:
    """Process-local live invocation guard; intentionally not a billing/spend cap."""

    def __init__(self, limit: int) -> None:
        if limit <= 0:
            raise ValueError("model call budget must be positive")
        self.limit = limit
        self._remaining = limit
        self._lock = Lock()

    @property
    def remaining(self) -> int:
        with self._lock:
            return self._remaining

    def reserve(self) -> None:
        with self._lock:
            if self._remaining <= 0:
                raise AgentExecutionError(
                    "live model call budget exhausted; request blocked before provider invocation"
                )
            self._remaining -= 1


class BudgetedExecutor:
    """Wrap a live executor with a process-local fail-closed invocation budget."""

    def __init__(self, inner: FleetExecutor, budget: ModelCallBudget) -> None:
        if not inner.is_live_google:
            raise ValueError("BudgetedExecutor is only for live Google execution")
        self._inner = inner
        self._budget = budget
        self.provider_name = inner.provider_name
        self.model_name = inner.model_name
        self.is_live_google = True

    @property
    def remaining_model_calls(self) -> int:
        return self._budget.remaining

    def execute(
        self,
        *,
        run_id: str,
        checkpoint_id: str,
        prompt: str,
    ) -> AgentExecutionReceipt:
        self._budget.reserve()
        return self._inner.execute(
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            prompt=prompt,
        )


class DeterministicExecutor:
    """Credential-free executor for graph/unit tests; never presented as Gemini execution."""

    provider_name = "deterministic_test"
    model_name: str | None = None
    is_live_google = False

    _OUTPUTS: dict[str, dict[str, Any]] = {
        "statistician": {
            "claim": "bounded quantitative signal",
            "evidence_ids": ["fixture_snapshot", "history_snapshot"],
            "confidence": 0.62,
        },
        "scout": {
            "claim": "bounded context signal",
            "evidence_ids": ["fixture_snapshot"],
            "confidence": 0.58,
        },
        "skeptic": {
            "claim": "challenge unsupported certainty",
            "evidence_ids": ["statistician", "scout"],
            "confidence": 0.71,
        },
        "orchestrator": {
            "claim": "provisional research verdict",
            "evidence_ids": ["statistician", "scout", "skeptic"],
            "confidence": 0.64,
        },
    }

    def execute(
        self,
        *,
        run_id: str,
        checkpoint_id: str,
        prompt: str,
    ) -> AgentExecutionReceipt:
        del run_id, prompt
        try:
            output = self._OUTPUTS[checkpoint_id]
        except KeyError as exc:
            raise AgentExecutionError(f"no deterministic agent output for {checkpoint_id}") from exc
        start = perf_counter_ns()
        copied = json.loads(json.dumps(output))
        elapsed_us = max(1, (perf_counter_ns() - start) // 1_000)
        return AgentExecutionReceipt(
            checkpoint_id=checkpoint_id,
            agent_id=checkpoint_id,
            provider=self.provider_name,
            model=None,
            structured_output=copied,
            elapsed_us=elapsed_us,
        )


_LIVE_BUDGET: ModelCallBudget | None = None
_LIVE_BUDGET_LOCK = Lock()


def _live_model_call_budget() -> ModelCallBudget:
    global _LIVE_BUDGET
    if _LIVE_BUDGET is not None:
        return _LIVE_BUDGET
    with _LIVE_BUDGET_LOCK:
        if _LIVE_BUDGET is None:
            raw_limit = os.getenv("RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET", "64").strip()
            try:
                limit = int(raw_limit)
            except ValueError as exc:
                raise ExecutionUnavailable(
                    "RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET must be a positive integer"
                ) from exc
            try:
                _LIVE_BUDGET = ModelCallBudget(limit)
            except ValueError as exc:
                raise ExecutionUnavailable(str(exc)) from exc
    return _LIVE_BUDGET


def executor_from_environment() -> FleetExecutor:
    mode = os.getenv("RECOVERY_MESH_EXECUTION_MODE", "deterministic").strip().lower()
    if mode in {"deterministic", "test", "local"}:
        return DeterministicExecutor()
    if mode in {"google", "google_adk", "vertex", "vertex_adk"}:
        from .google_adk import GoogleAdkExecutor

        return BudgetedExecutor(GoogleAdkExecutor(), _live_model_call_budget())
    raise ExecutionUnavailable(f"unsupported RECOVERY_MESH_EXECUTION_MODE={mode!r}")
