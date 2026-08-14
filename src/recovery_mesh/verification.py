from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from .hashing import sha256_digest
from .models import Checkpoint, TrustBreak, TrustBreakClass


class WorkerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str
    evidence_ids: list[str]
    confidence: float


class VerificationFailure(ValueError):
    pass


def verify_integrity(checkpoint: Checkpoint, structured_output: Any) -> None:
    actual = sha256_digest(structured_output)
    if actual != checkpoint.structured_output_digest:
        raise VerificationFailure("structured output digest mismatch")


def detect_stale_evidence(
    *,
    run_id: str,
    checkpoint_id: str,
    observed_at: datetime,
    max_age: timedelta,
    now: datetime | None = None,
    controlled: bool = False,
) -> TrustBreak | None:
    reference = now or datetime.now(UTC)
    normalized = observed_at if observed_at.tzinfo else observed_at.replace(tzinfo=UTC)
    age = reference - normalized
    if age <= max_age:
        return None
    return TrustBreak(
        break_id=f"stale:{checkpoint_id}:{int(reference.timestamp())}",
        run_id=run_id,
        checkpoint_id=checkpoint_id,
        break_class=TrustBreakClass.EVIDENCE,
        reason_code="STALE_EVIDENCE",
        reason=f"evidence age {age} exceeds maximum {max_age}",
        controlled=controlled,
        evidence={"age_seconds": age.total_seconds(), "max_age_seconds": max_age.total_seconds()},
    )


def detect_policy_drift(
    *,
    run_id: str,
    checkpoint_id: str,
    checkpoint_policy_version: str,
    active_policy_version: str,
    controlled: bool = False,
) -> TrustBreak | None:
    if checkpoint_policy_version == active_policy_version:
        return None
    return TrustBreak(
        break_id=f"policy:{checkpoint_id}:{active_policy_version}",
        run_id=run_id,
        checkpoint_id=checkpoint_id,
        break_class=TrustBreakClass.POLICY,
        reason_code="POLICY_VERSION_DRIFT",
        reason=(
            f"checkpoint policy {checkpoint_policy_version} differs from active policy "
            f"{active_policy_version}"
        ),
        controlled=controlled,
        evidence={
            "checkpoint_policy_version": checkpoint_policy_version,
            "active_policy_version": active_policy_version,
        },
    )


def detect_malformed_worker_output(
    *,
    run_id: str,
    checkpoint_id: str,
    payload: Any,
    controlled: bool = False,
) -> TrustBreak | None:
    try:
        WorkerOutput.model_validate(payload)
    except ValidationError as exc:
        return TrustBreak(
            break_id=f"malformed:{checkpoint_id}",
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            break_class=TrustBreakClass.AGENT,
            reason_code="MALFORMED_WORKER_OUTPUT",
            reason="worker output failed the strict structured-output contract",
            controlled=controlled,
            evidence={"validation_error_count": exc.error_count()},
        )
    return None
