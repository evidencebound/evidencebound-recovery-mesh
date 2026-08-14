from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrustStatus(StrEnum):
    VERIFIED = "VERIFIED"
    INVALIDATED = "INVALIDATED"
    RECOMPUTE = "RECOMPUTE"
    BLOCKED = "BLOCKED"


class CheckpointKind(StrEnum):
    EVIDENCE = "EVIDENCE"
    AGENT = "AGENT"
    POLICY = "POLICY"
    ACTION = "ACTION"


class IntegrityMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    algorithm: str = "sha256"
    digest: str


class ProvenanceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_class: str
    source_ref: str | None = None
    observed_at: datetime | None = None
    controlled_fixture: bool = False


class Checkpoint(BaseModel):
    """Immutable checkpoint payload plus mutable trust status represented by replacement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    checkpoint_id: str
    kind: CheckpointKind
    agent_id: str | None = None
    agent_version: str | None = None
    dependency_checkpoint_ids: tuple[str, ...] = ()
    input_digests: tuple[str, ...] = ()
    evidence_digests: tuple[str, ...] = ()
    tool_result_digests: tuple[str, ...] = ()
    policy_version: str
    structured_output_digest: str
    verification_status: TrustStatus = TrustStatus.VERIFIED
    integrity: IntegrityMetadata
    provenance: ProvenanceMetadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    verified_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    side_effect_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_semantics(self) -> "Checkpoint":
        if self.kind is CheckpointKind.AGENT and (not self.agent_id or not self.agent_version):
            raise ValueError("agent checkpoints require agent_id and agent_version")
        if self.kind is CheckpointKind.ACTION and not self.side_effect_key:
            raise ValueError("action checkpoints require side_effect_key")
        if self.integrity.digest != self.structured_output_digest:
            raise ValueError("integrity digest must bind the structured output digest")
        if self.verification_status is TrustStatus.VERIFIED and self.verified_at is None:
            raise ValueError("VERIFIED checkpoints require verified_at")
        return self


class TrustBreakClass(StrEnum):
    EVIDENCE = "EVIDENCE"
    POLICY = "POLICY"
    AGENT = "AGENT"
    SECURITY = "SECURITY"


class TrustBreak(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    break_id: str
    run_id: str
    checkpoint_id: str
    break_class: TrustBreakClass
    reason_code: str
    reason: str
    controlled: bool = False
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evidence: dict[str, Any] = Field(default_factory=dict)
