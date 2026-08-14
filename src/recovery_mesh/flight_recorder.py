from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    RUN_STARTED = "RUN_STARTED"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"
    TRUST_BREAK_DETECTED = "TRUST_BREAK_DETECTED"
    BLAST_RADIUS_COMPUTED = "BLAST_RADIUS_COMPUTED"
    ACTION_BLOCKED = "ACTION_BLOCKED"
    CHECKPOINT_REUSED = "CHECKPOINT_REUSED"
    RECOMPUTE_STARTED = "RECOMPUTE_STARTED"
    CHECKPOINT_REVERIFIED = "CHECKPOINT_REVERIFIED"
    ACTION_RESUMED = "ACTION_RESUMED"
    RECOVERY_COMPLETED = "RECOVERY_COMPLETED"


class FlightEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: int
    run_id: str
    event_type: EventType
    checkpoint_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
