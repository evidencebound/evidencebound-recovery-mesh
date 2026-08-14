from __future__ import annotations

import pytest

import recovery_mesh.execution as execution_module
from recovery_mesh.execution import (
    AgentExecutionError,
    AgentExecutionReceipt,
    BudgetedExecutor,
    DeterministicExecutor,
    ExecutionUnavailable,
    ModelCallBudget,
    executor_from_environment,
)
from recovery_mesh.runtime import DemoRun


class RecordingGoogleExecutor:
    provider_name = "google_adk_vertex"
    model_name = "gemini-3.5-flash"
    is_live_google = True

    def __init__(self) -> None:
        self.calls: list[str] = []

    def execute(self, *, run_id: str, checkpoint_id: str, prompt: str) -> AgentExecutionReceipt:
        assert "Use only the bounded JSON inputs" in prompt
        self.calls.append(checkpoint_id)
        dependencies = {
            "statistician": ["fixture_snapshot", "history_snapshot"],
            "scout": ["fixture_snapshot"],
            "skeptic": ["statistician", "scout"],
            "orchestrator": ["statistician", "scout", "skeptic"],
        }[checkpoint_id]
        return AgentExecutionReceipt(
            checkpoint_id=checkpoint_id,
            agent_id=checkpoint_id,
            provider=self.provider_name,
            model=self.model_name,
            structured_output={
                "claim": f"bounded {checkpoint_id} output",
                "evidence_ids": dependencies,
                "confidence": 0.5,
            },
            elapsed_us=1000,
            model_calls=1,
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            invocation_ids=(f"inv-{run_id}-{len(self.calls)}",),
            event_authors=(checkpoint_id,),
        )


def test_live_execution_receipts_drive_measured_selective_recovery() -> None:
    executor = RecordingGoogleExecutor()
    run = DemoRun("live-test", executor=executor)
    assert executor.calls == ["statistician", "scout", "skeptic", "orchestrator"]
    snapshot = run.snapshot()
    assert snapshot["execution"]["live_google"] is True
    assert len(snapshot["execution"]["baseline"]) == 4

    run.inject_fault("stale_evidence")
    receipt = run.recover()

    assert receipt.measurement_class == "google_adk_live_with_usage"
    assert receipt.selective_recovery_agent_executions == 3
    assert receipt.full_restart_agent_executions == 4
    assert receipt.selective_recovery_model_calls == 3
    assert receipt.full_restart_model_calls == 4
    assert receipt.selective_recovery_input_tokens == 300
    assert receipt.full_restart_input_tokens == 400
    assert receipt.model_call_reduction_ratio == 0.25
    assert receipt.input_token_reduction_ratio == 0.25
    assert len(run.snapshot()["execution"]["recovery"]) == 3


def test_agent_checkpoint_input_digests_bind_actual_parent_outputs() -> None:
    run = DemoRun("digest-test")
    graph = run.engine.graph
    statistician = graph.checkpoint("statistician")
    assert statistician.input_digests == (
        graph.checkpoint("fixture_snapshot").structured_output_digest,
        graph.checkpoint("history_snapshot").structured_output_digest,
    )

    old_history_digest = graph.checkpoint("history_snapshot").structured_output_digest
    run.inject_fault("stale_evidence")
    run.recover()
    graph = run.engine.graph
    new_history_digest = graph.checkpoint("history_snapshot").structured_output_digest
    assert new_history_digest != old_history_digest
    assert graph.checkpoint("statistician").input_digests[1] == new_history_digest


def test_budgeted_executor_blocks_before_third_provider_call() -> None:
    inner = RecordingGoogleExecutor()
    budget = ModelCallBudget(2)
    executor = BudgetedExecutor(inner, budget)

    assert executor.provider_name == "google_adk_vertex"
    assert executor.model_name == "gemini-3.5-flash"
    assert executor.is_live_google is True
    assert executor.remaining_model_calls == 2

    call = {
        "run_id": "budget",
        "checkpoint_id": "scout",
        "prompt": "Use only the bounded JSON inputs",
    }
    executor.execute(**call)
    executor.execute(**call)
    assert executor.remaining_model_calls == 0
    assert inner.calls == ["scout", "scout"]

    with pytest.raises(AgentExecutionError, match="budget exhausted"):
        executor.execute(**call)
    assert inner.calls == ["scout", "scout"]


def test_live_budget_configuration_wraps_google_executor(monkeypatch) -> None:
    import recovery_mesh.google_adk as google_adk_module

    monkeypatch.setenv("RECOVERY_MESH_EXECUTION_MODE", "google_adk")
    monkeypatch.setenv("RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET", "7")
    monkeypatch.setattr(execution_module, "_LIVE_BUDGET", None)
    monkeypatch.setattr(google_adk_module, "GoogleAdkExecutor", RecordingGoogleExecutor)

    executor = executor_from_environment()
    assert isinstance(executor, BudgetedExecutor)
    assert executor.remaining_model_calls == 7


def test_invalid_live_budget_configuration_fails_closed(monkeypatch) -> None:
    import recovery_mesh.google_adk as google_adk_module

    monkeypatch.setenv("RECOVERY_MESH_EXECUTION_MODE", "google_adk")
    monkeypatch.setenv("RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET", "zero")
    monkeypatch.setattr(execution_module, "_LIVE_BUDGET", None)
    monkeypatch.setattr(google_adk_module, "GoogleAdkExecutor", RecordingGoogleExecutor)
    with pytest.raises(ExecutionUnavailable, match="positive integer"):
        executor_from_environment()

    monkeypatch.setenv("RECOVERY_MESH_LIVE_MODEL_CALL_BUDGET", "0")
    monkeypatch.setattr(execution_module, "_LIVE_BUDGET", None)
    with pytest.raises(ExecutionUnavailable, match="must be positive"):
        executor_from_environment()


def test_budget_wrapper_rejects_non_live_executor() -> None:
    with pytest.raises(ValueError, match="only for live Google"):
        BudgetedExecutor(DeterministicExecutor(), ModelCallBudget(1))
    with pytest.raises(ValueError, match="must be positive"):
        ModelCallBudget(0)


def test_invalid_execution_mode_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("RECOVERY_MESH_EXECUTION_MODE", "not-a-provider")
    with pytest.raises(ExecutionUnavailable):
        executor_from_environment()
