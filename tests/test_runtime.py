from __future__ import annotations

import pytest

from recovery_mesh.flight_recorder import EventType
from recovery_mesh.runtime import DemoRun, UnsupportedScenario


def _status(snapshot: dict[str, object], checkpoint_id: str) -> str:
    checkpoints = snapshot["checkpoints"]
    assert isinstance(checkpoints, list)
    return next(item["status"] for item in checkpoints if item["checkpoint_id"] == checkpoint_id)


def test_stale_evidence_judge_moment_and_selective_recovery() -> None:
    run = DemoRun("r-stale")
    plan = run.inject_fault("stale_evidence")
    assert plan.blast_radius.blocked_action_nodes == ("publish_action",)
    snapshot = run.snapshot()
    assert _status(snapshot, "scout") == "VERIFIED"
    assert _status(snapshot, "publish_action") == "BLOCKED"

    receipt = run.recover()
    final = run.snapshot()
    assert receipt.full_restart_agent_executions == 4
    assert receipt.selective_recovery_agent_executions == 3
    assert receipt.reused_agent_checkpoints == 1
    assert receipt.model_calls is None
    assert receipt.measurement_class == "deterministic_core_only"
    assert _status(final, "publish_action") == "VERIFIED"
    event_types = [event.event_type for event in run.events]
    assert EventType.TRUST_BREAK_DETECTED in event_types
    assert EventType.ACTION_BLOCKED in event_types
    assert EventType.CHECKPOINT_REUSED in event_types
    assert EventType.RECOVERY_COMPLETED in event_types


def test_malformed_worker_reuses_statistician() -> None:
    run = DemoRun("r-malformed")
    plan = run.inject_fault("malformed_worker")
    assert "statistician" in plan.blast_radius.reusable_checkpoints
    assert "scout" in plan.blast_radius.recomputation_set
    receipt = run.recover()
    assert receipt.selective_recovery_agent_executions == 3
    assert receipt.reused_agent_checkpoints == 1


def test_policy_drift_recomputes_policy_and_orchestrator_only() -> None:
    run = DemoRun("r-policy")
    plan = run.inject_fault("policy_drift")
    assert plan.blast_radius.recomputation_set == ("policy_rules", "orchestrator")
    assert set(plan.blast_radius.reusable_checkpoints) >= {
        "statistician",
        "scout",
        "skeptic",
    }
    receipt = run.recover()
    assert receipt.selective_recovery_agent_executions == 1
    assert receipt.reused_agent_checkpoints == 3


def test_unsupported_fault_is_rejected() -> None:
    run = DemoRun("r")
    with pytest.raises(UnsupportedScenario):
        run.inject_fault("not-real")
