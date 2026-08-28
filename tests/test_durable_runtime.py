from __future__ import annotations

import importlib.util


def test_runtime_can_accept_a_run_store() -> None:
    spec = importlib.util.find_spec("recovery_mesh.persistence")
    assert spec is not None, "persistence module must exist before durable runtime wiring"

    from recovery_mesh.persistence import InMemoryRunStore
    from recovery_mesh.runtime import DemoRun

    store = InMemoryRunStore()
    run = DemoRun(store=store)

    durable = store.load_run_snapshot(run.run_id)
    assert durable is not None
    assert durable["run_id"] == run.run_id
    assert durable["persistence"]["provider"] == "memory"


def test_blocked_action_never_creates_durable_receipt() -> None:
    from recovery_mesh.persistence import InMemoryRunStore
    from recovery_mesh.runtime import DemoRun

    store = InMemoryRunStore()
    run = DemoRun("run-durable-blocked", store=store)
    plan = run.inject_fault("stale_evidence")

    assert plan.blast_radius.blocked_action_nodes == ("publish_action",)
    durable = run.durable_snapshot()
    assert durable is not None
    assert durable["action_receipt"] is None
    assert durable["rehydration"]["trusted"] is True


def test_policy_drift_recovery_persists_new_policy_and_rehydrates_trusted() -> None:
    from recovery_mesh.persistence import InMemoryRunStore
    from recovery_mesh.runtime import DemoRun

    store = InMemoryRunStore()
    run = DemoRun("run-durable-policy", store=store)
    run.inject_fault("policy_drift")
    run.recover()

    durable = run.durable_snapshot()
    assert durable is not None
    snapshot = durable["snapshot"]
    assert snapshot["active_policy_version"] == "policy-v2"
    assert durable["action_receipt"] is not None
    assert durable["rehydration"]["trusted"] is True
    assert durable["rehydration"]["failures"] == []
