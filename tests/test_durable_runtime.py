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
