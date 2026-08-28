from datetime import UTC, datetime

from recovery_mesh.persistence import verify_persisted_snapshot
from recovery_mesh.recovery import SideEffectReceipt


def test_blocked_action_with_durable_receipt_is_never_trusted() -> None:
    snapshot = {
        "run_id": "run-crash-window",
        "active_policy_version": "policy-v1",
        "checkpoints": [
            {
                "checkpoint_id": "publish_action",
                "kind": "ACTION",
                "dependencies": [],
                "input_digests": [],
                "evidence_digests": [],
                "tool_result_digests": [],
                "output_digest": "digest-action",
                "integrity_digest": "digest-action",
                "status": "BLOCKED",
                "policy_version": "policy-v1",
                "side_effect_key": "run-crash-window:publish",
            }
        ],
        "events": [],
        "action_receipt": None,
    }
    receipt = SideEffectReceipt(
        side_effect_key="run-crash-window:publish",
        payload_digest="digest-committed",
        committed_at=datetime.now(UTC),
        duplicate_suppressed=False,
    )

    result = verify_persisted_snapshot(snapshot, receipt)

    assert result.trusted is False
    assert any("BLOCKED" in failure and "receipt" in failure for failure in result.failures)
