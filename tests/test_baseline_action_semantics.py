from recovery_mesh.persistence import InMemoryRunStore
from recovery_mesh.runtime import DemoRun
from recovery_mesh.workload import baseline_source_outputs


def test_baseline_action_output_does_not_claim_external_commit() -> None:
    output = baseline_source_outputs()["publish_action"]

    assert output.get("published") is not True
    assert output == {"state": "eligible_not_committed"}


def test_verified_baseline_has_no_action_receipt_until_recovery_commit() -> None:
    store = InMemoryRunStore()
    run = DemoRun("run-baseline-no-side-effect", store=store)

    snapshot = run.snapshot()
    action = next(
        checkpoint
        for checkpoint in snapshot["checkpoints"]
        if checkpoint["checkpoint_id"] == "publish_action"
    )
    assert action["status"] == "VERIFIED"
    assert snapshot["action_receipt"] is None
    assert snapshot["persistence"]["action_receipt_committed"] is False
