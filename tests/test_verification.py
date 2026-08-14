from __future__ import annotations

from datetime import UTC, datetime, timedelta

from recovery_mesh.models import TrustBreakClass
from recovery_mesh.verification import (
    detect_malformed_worker_output,
    detect_policy_drift,
    detect_stale_evidence,
)


def test_stale_evidence_is_a_distinct_trust_break() -> None:
    now = datetime(2026, 8, 14, tzinfo=UTC)
    result = detect_stale_evidence(
        run_id="r",
        checkpoint_id="evidence",
        observed_at=now - timedelta(hours=3),
        max_age=timedelta(hours=1),
        now=now,
        controlled=True,
    )
    assert result is not None
    assert result.break_class is TrustBreakClass.EVIDENCE
    assert result.reason_code == "STALE_EVIDENCE"
    assert result.controlled


def test_fresh_evidence_passes() -> None:
    now = datetime(2026, 8, 14, tzinfo=UTC)
    assert (
        detect_stale_evidence(
            run_id="r",
            checkpoint_id="evidence",
            observed_at=now - timedelta(minutes=5),
            max_age=timedelta(hours=1),
            now=now,
        )
        is None
    )


def test_policy_drift_is_detected() -> None:
    result = detect_policy_drift(
        run_id="r",
        checkpoint_id="orchestrator",
        checkpoint_policy_version="policy-v1",
        active_policy_version="policy-v2",
        controlled=True,
    )
    assert result is not None
    assert result.break_class is TrustBreakClass.POLICY
    assert result.reason_code == "POLICY_VERSION_DRIFT"


def test_malformed_agent_output_is_distinct_from_evidence_failure() -> None:
    result = detect_malformed_worker_output(
        run_id="r",
        checkpoint_id="scout",
        payload={"claim": "unsupported", "confidence": "not-a-number"},
        controlled=True,
    )
    assert result is not None
    assert result.break_class is TrustBreakClass.AGENT
    assert result.reason_code == "MALFORMED_WORKER_OUTPUT"


def test_valid_agent_output_passes_strict_contract() -> None:
    result = detect_malformed_worker_output(
        run_id="r",
        checkpoint_id="scout",
        payload={"claim": "bounded", "evidence_ids": ["fixture"], "confidence": 0.5},
    )
    assert result is None
