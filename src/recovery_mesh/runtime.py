from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from time import perf_counter_ns
from typing import Any, Iterable
from uuid import uuid4

from .execution import (
    AgentExecutionError,
    AgentExecutionReceipt,
    FleetExecutor,
    executor_from_environment,
)
from .flight_recorder import EventType, FlightEvent
from .graph import TrustGraph
from .models import CheckpointKind, ProvenanceMetadata, TrustBreak, TrustStatus
from .recovery import RecoveryEngine, RecoveryPlan, SideEffectLedger
from .verification import (
    detect_malformed_worker_output,
    detect_policy_drift,
    detect_stale_evidence,
)
from .workload import (
    AGENT_DEPENDENCIES,
    AGENT_ORDER,
    POLICY_VERSION,
    baseline_source_outputs,
    build_agent_prompt,
    build_demo_checkpoints,
)


class UnsupportedScenario(ValueError):
    pass


@dataclass(frozen=True)
class BenchmarkReceipt:
    scenario: str
    full_restart_agent_executions: int
    selective_recovery_agent_executions: int
    reused_agent_checkpoints: int
    full_restart_elapsed_us: int
    selective_recovery_elapsed_us: int
    full_restart_model_calls: int | None = None
    selective_recovery_model_calls: int | None = None
    full_restart_input_tokens: int | None = None
    selective_recovery_input_tokens: int | None = None
    full_restart_output_tokens: int | None = None
    selective_recovery_output_tokens: int | None = None
    measurement_class: str = "deterministic_core_only"

    @property
    def model_calls(self) -> int | None:
        return self.selective_recovery_model_calls

    @property
    def input_tokens(self) -> int | None:
        return self.selective_recovery_input_tokens

    @property
    def output_tokens(self) -> int | None:
        return self.selective_recovery_output_tokens

    @property
    def execution_reduction_ratio(self) -> float:
        if self.full_restart_agent_executions == 0:
            return 0.0
        return 1 - (
            self.selective_recovery_agent_executions / self.full_restart_agent_executions
        )

    @property
    def model_call_reduction_ratio(self) -> float | None:
        if not self.full_restart_model_calls:
            return None
        if self.selective_recovery_model_calls is None:
            return None
        return 1 - (self.selective_recovery_model_calls / self.full_restart_model_calls)

    @property
    def input_token_reduction_ratio(self) -> float | None:
        if not self.full_restart_input_tokens:
            return None
        if self.selective_recovery_input_tokens is None:
            return None
        return 1 - (self.selective_recovery_input_tokens / self.full_restart_input_tokens)


class DemoRun:
    """Bounded judge workload; models advise while deterministic trust contracts decide."""

    def __init__(
        self,
        run_id: str | None = None,
        *,
        executor: FleetExecutor | None = None,
    ):
        self.run_id = run_id or f"run-{uuid4().hex[:12]}"
        self.executor = executor or executor_from_environment()
        self.ledger = SideEffectLedger()
        self.events: list[FlightEvent] = []
        self._event_seq = 0
        self.active_plan: RecoveryPlan | None = None
        self.active_scenario: str | None = None
        self.active_policy_version = POLICY_VERSION
        self.benchmark: BenchmarkReceipt | None = None
        self._outputs = baseline_source_outputs()
        self.baseline_execution_receipts: list[AgentExecutionReceipt] = []
        self.recovery_execution_receipts: list[AgentExecutionReceipt] = []

        provenance: dict[str, dict[str, Any]] = {}
        for agent_id in AGENT_ORDER:
            receipt = self._execute_agent(agent_id)
            self.baseline_execution_receipts.append(receipt)
            self._outputs[agent_id] = receipt.structured_output
            provenance[agent_id] = self._provenance_info(receipt)

        self.engine = RecoveryEngine(
            TrustGraph(
                build_demo_checkpoints(
                    self.run_id,
                    outputs=self._outputs,
                    agent_provenance=provenance,
                    policy_version=self.active_policy_version,
                )
            )
        )
        self._record(
            EventType.RUN_STARTED,
            "Agent fleet completed a verified baseline run.",
            data={
                "execution_provider": self.executor.provider_name,
                "model": self.executor.model_name,
                "live_google": self.executor.is_live_google,
            },
        )
        for checkpoint in self.engine.graph.checkpoints:
            self._record(
                EventType.CHECKPOINT_VERIFIED,
                f"{checkpoint.checkpoint_id} verified.",
                checkpoint_id=checkpoint.checkpoint_id,
                data={"kind": checkpoint.kind.value},
            )

    def inject_fault(self, scenario: str) -> RecoveryPlan:
        if self.active_plan is not None:
            raise RuntimeError("a trust break is already active")
        trust_break = self._detect_controlled_fault(scenario)
        plan = self.engine.plan(trust_break)
        self.engine.apply_plan(plan)
        self.active_plan = plan
        self.active_scenario = scenario
        if scenario == "policy_drift":
            self.active_policy_version = "policy-v2"

        self._record(
            EventType.TRUST_BREAK_DETECTED,
            f"TRUST BREAK DETECTED: {trust_break.reason_code}",
            checkpoint_id=trust_break.checkpoint_id,
            data={
                "break_class": trust_break.break_class.value,
                "reason": trust_break.reason,
                "controlled": trust_break.controlled,
            },
        )
        self._record(
            EventType.BLAST_RADIUS_COMPUTED,
            "Exact downstream trust blast radius computed deterministically.",
            checkpoint_id=trust_break.checkpoint_id,
            data={
                "contaminated": list(plan.blast_radius.contaminated_checkpoints),
                "recompute": list(plan.blast_radius.recomputation_set),
                "reusable": list(plan.blast_radius.reusable_checkpoints),
                "blocked_actions": list(plan.blast_radius.blocked_action_nodes),
            },
        )
        for checkpoint_id in plan.blast_radius.blocked_action_nodes:
            self._record(
                EventType.ACTION_BLOCKED,
                "Unsafe downstream action frozen before side effect.",
                checkpoint_id=checkpoint_id,
            )
        for checkpoint_id in plan.blast_radius.reusable_checkpoints:
            self._record(
                EventType.CHECKPOINT_REUSED,
                "Still-verifiable checkpoint preserved; no rerun scheduled.",
                checkpoint_id=checkpoint_id,
            )
        return plan

    def recover(self) -> BenchmarkReceipt:
        if self.active_plan is None or self.active_scenario is None:
            raise RuntimeError("no active trust break")
        plan = self.active_plan
        scenario = self.active_scenario
        self.recovery_execution_receipts = []

        selective_start = perf_counter_ns()
        agent_reruns = 0
        for checkpoint_id in plan.rerun_order:
            checkpoint = self.engine.graph.checkpoint(checkpoint_id)
            self._record(
                EventType.RECOMPUTE_STARTED,
                "Recomputation started after all reusable dependencies passed trust gates.",
                checkpoint_id=checkpoint_id,
            )
            if checkpoint.kind is CheckpointKind.AGENT:
                agent_reruns += 1
                receipt = self._execute_agent(checkpoint_id)
                self.recovery_execution_receipts.append(receipt)
                output = receipt.structured_output
                provenance = ProvenanceMetadata(
                    source_class=receipt.provider,
                    source_ref=receipt.source_ref,
                    observed_at=datetime.now(UTC),
                    controlled_fixture=False,
                )
                metadata = self._receipt_metadata(receipt)
            else:
                output = self._corrected_non_agent_output(checkpoint_id)
                provenance = checkpoint.provenance.model_copy(
                    update={
                        "source_ref": (
                            f"policy://{self.active_policy_version}"
                            if checkpoint.kind is CheckpointKind.POLICY
                            else checkpoint.provenance.source_ref
                        ),
                        "observed_at": datetime.now(UTC),
                    }
                )
                metadata = checkpoint.metadata
            self._outputs[checkpoint_id] = output
            input_digests, evidence_digests = self._current_dependency_digests(checkpoint_id)
            self.engine.verify_recomputed(
                checkpoint_id,
                structured_output=output,
                input_digests=input_digests,
                evidence_digests=evidence_digests,
                policy_version=self.active_policy_version,
                provenance=provenance,
                metadata=metadata,
            )
            self._record(
                EventType.CHECKPOINT_REVERIFIED,
                "Recomputed checkpoint passed deterministic verification.",
                checkpoint_id=checkpoint_id,
                data={
                    "execution_provider": (
                        self.executor.provider_name
                        if checkpoint.kind is CheckpointKind.AGENT
                        else "deterministic"
                    )
                },
            )
        payload = {"run_id": self.run_id, "verdict": "verified_recovery", "safe": True}
        for action_id in plan.blast_radius.blocked_action_nodes:
            receipt = self.engine.resume_action(action_id, payload=payload, ledger=self.ledger)
            self._outputs[action_id] = payload
            self._record(
                EventType.ACTION_RESUMED,
                "Previously blocked action resumed after all dependencies became VERIFIED.",
                checkpoint_id=action_id,
                data={"duplicate_suppressed": receipt.duplicate_suppressed},
            )
        selective_elapsed = max(1, (perf_counter_ns() - selective_start) // 1_000)

        full_elapsed, full_receipts = self._measure_full_restart()
        reusable_agents = sum(
            1
            for checkpoint_id in plan.blast_radius.reusable_checkpoints
            if self.engine.graph.checkpoint(checkpoint_id).kind is CheckpointKind.AGENT
        )
        selective_usage = _aggregate_usage(self.recovery_execution_receipts)
        full_usage = _aggregate_usage(full_receipts)
        if self.executor.is_live_google:
            measurement_class = (
                "google_adk_live_with_usage"
                if full_usage["model_calls"] is not None
                and selective_usage["model_calls"] is not None
                else "google_adk_live_usage_partial"
            )
        else:
            measurement_class = "deterministic_core_only"

        self.benchmark = BenchmarkReceipt(
            scenario=scenario,
            full_restart_agent_executions=len(AGENT_ORDER),
            selective_recovery_agent_executions=agent_reruns,
            reused_agent_checkpoints=reusable_agents,
            full_restart_elapsed_us=full_elapsed,
            selective_recovery_elapsed_us=selective_elapsed,
            full_restart_model_calls=full_usage["model_calls"],
            selective_recovery_model_calls=selective_usage["model_calls"],
            full_restart_input_tokens=full_usage["input_tokens"],
            selective_recovery_input_tokens=selective_usage["input_tokens"],
            full_restart_output_tokens=full_usage["output_tokens"],
            selective_recovery_output_tokens=selective_usage["output_tokens"],
            measurement_class=measurement_class,
        )
        self._record(
            EventType.RECOVERY_COMPLETED,
            "Selective recovery completed and final action is VERIFIED.",
            data={
                "agent_reruns": agent_reruns,
                "reused_agent_checkpoints": reusable_agents,
                "measurement_class": self.benchmark.measurement_class,
                "full_restart_model_calls": self.benchmark.full_restart_model_calls,
                "selective_recovery_model_calls": self.benchmark.selective_recovery_model_calls,
            },
        )
        self.active_plan = None
        self.active_scenario = None
        return self.benchmark

    def snapshot(self) -> dict[str, Any]:
        active_blast = None
        if self.active_plan is not None:
            blast = self.active_plan.blast_radius
            active_blast = {
                "invalidated_source": blast.invalidated_source,
                "contaminated_checkpoints": list(blast.contaminated_checkpoints),
                "recomputation_set": list(blast.recomputation_set),
                "blocked_action_nodes": list(blast.blocked_action_nodes),
                "reusable_checkpoints": list(blast.reusable_checkpoints),
            }
        benchmark = None
        if self.benchmark is not None:
            benchmark = asdict(self.benchmark)
            benchmark.update(
                {
                    "model_calls": self.benchmark.model_calls,
                    "input_tokens": self.benchmark.input_tokens,
                    "output_tokens": self.benchmark.output_tokens,
                    "execution_reduction_ratio": self.benchmark.execution_reduction_ratio,
                    "model_call_reduction_ratio": self.benchmark.model_call_reduction_ratio,
                    "input_token_reduction_ratio": self.benchmark.input_token_reduction_ratio,
                }
            )
        return {
            "run_id": self.run_id,
            "execution": {
                "provider": self.executor.provider_name,
                "model": self.executor.model_name,
                "live_google": self.executor.is_live_google,
                "baseline": [self._public_receipt(item) for item in self.baseline_execution_receipts],
                "recovery": [self._public_receipt(item) for item in self.recovery_execution_receipts],
            },
            "checkpoints": [
                {
                    "checkpoint_id": item.checkpoint_id,
                    "kind": item.kind.value,
                    "agent_id": item.agent_id,
                    "dependencies": list(item.dependency_checkpoint_ids),
                    "input_digests": list(item.input_digests),
                    "evidence_digests": list(item.evidence_digests),
                    "output_digest": item.structured_output_digest,
                    "status": item.verification_status.value,
                    "policy_version": item.policy_version,
                    "provenance": item.provenance.model_dump(mode="json"),
                    "metadata": item.metadata,
                }
                for item in self.engine.graph.checkpoints
            ],
            "active_blast_radius": active_blast,
            "events": [event.model_dump(mode="json") for event in self.events],
            "benchmark": benchmark,
        }

    def _execute_agent(self, checkpoint_id: str) -> AgentExecutionReceipt:
        prompt = build_agent_prompt(checkpoint_id, self._outputs)
        receipt = self.executor.execute(
            run_id=self.run_id,
            checkpoint_id=checkpoint_id,
            prompt=prompt,
        )
        malformed = detect_malformed_worker_output(
            run_id=self.run_id,
            checkpoint_id=checkpoint_id,
            payload=receipt.structured_output,
            controlled=False,
        )
        if malformed is not None:
            raise AgentExecutionError(
                f"{checkpoint_id} failed strict worker contract: {malformed.reason_code}"
            )
        references = set(receipt.structured_output.get("evidence_ids", []))
        allowed = set(AGENT_DEPENDENCIES[checkpoint_id])
        unsupported = references - allowed
        if unsupported:
            raise AgentExecutionError(
                f"{checkpoint_id} cited unsupported dependency ids: {sorted(unsupported)}"
            )
        return receipt

    def _measure_full_restart(self) -> tuple[int, list[AgentExecutionReceipt]]:
        start = perf_counter_ns()
        if not self.executor.is_live_google:
            for checkpoint_id in AGENT_ORDER:
                self.executor.execute(
                    run_id="benchmark-full-restart",
                    checkpoint_id=checkpoint_id,
                    prompt=build_agent_prompt(checkpoint_id, self._outputs),
                )
            return max(1, (perf_counter_ns() - start) // 1_000), []

        benchmark_outputs = dict(self._outputs)
        receipts: list[AgentExecutionReceipt] = []
        for checkpoint_id in AGENT_ORDER:
            prompt = build_agent_prompt(checkpoint_id, benchmark_outputs)
            receipt = self.executor.execute(
                run_id=f"{self.run_id}-full-restart-benchmark",
                checkpoint_id=checkpoint_id,
                prompt=prompt,
            )
            malformed = detect_malformed_worker_output(
                run_id=self.run_id,
                checkpoint_id=checkpoint_id,
                payload=receipt.structured_output,
            )
            if malformed is not None:
                raise AgentExecutionError(
                    f"full-restart benchmark {checkpoint_id} failed structured contract"
                )
            benchmark_outputs[checkpoint_id] = receipt.structured_output
            receipts.append(receipt)
        return max(1, (perf_counter_ns() - start) // 1_000), receipts

    def _current_dependency_digests(self, checkpoint_id: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        checkpoint = self.engine.graph.checkpoint(checkpoint_id)
        input_digests = tuple(
            self.engine.graph.checkpoint(parent_id).structured_output_digest
            for parent_id in checkpoint.dependency_checkpoint_ids
        )
        evidence_digests = tuple(
            self.engine.graph.checkpoint(parent_id).structured_output_digest
            for parent_id in checkpoint.dependency_checkpoint_ids
            if self.engine.graph.checkpoint(parent_id).kind is CheckpointKind.EVIDENCE
        )
        return input_digests, evidence_digests

    def _detect_controlled_fault(self, scenario: str) -> TrustBreak:
        now = datetime.now(UTC)
        if scenario == "stale_evidence":
            result = detect_stale_evidence(
                run_id=self.run_id,
                checkpoint_id="history_snapshot",
                observed_at=now - timedelta(days=2),
                max_age=timedelta(hours=24),
                now=now,
                controlled=True,
            )
        elif scenario == "malformed_worker":
            result = detect_malformed_worker_output(
                run_id=self.run_id,
                checkpoint_id="scout",
                payload={"claim": "unsupported", "confidence": "NaN-not-number"},
                controlled=True,
            )
        elif scenario == "policy_drift":
            result = detect_policy_drift(
                run_id=self.run_id,
                checkpoint_id="policy_rules",
                checkpoint_policy_version=POLICY_VERSION,
                active_policy_version="policy-v2",
                controlled=True,
            )
        else:
            raise UnsupportedScenario(scenario)
        if result is None:
            raise RuntimeError(f"controlled scenario {scenario} failed to produce a trust break")
        return result

    def _corrected_non_agent_output(self, checkpoint_id: str) -> dict[str, Any]:
        if checkpoint_id == "history_snapshot":
            return {
                "sample_size": 20,
                "metric": "recent-form",
                "window": "controlled-history-v2",
                "fresh": True,
            }
        if checkpoint_id == "policy_rules":
            return {
                "policy_version": self.active_policy_version,
                "require_citations": True,
                "allow_publish_only_if_verified": True,
            }
        raise RuntimeError(f"no bounded non-agent recomputation for {checkpoint_id}")

    @staticmethod
    def _provenance_info(receipt: AgentExecutionReceipt) -> dict[str, Any]:
        return {
            "agent_version": "hackathon-v1",
            "source_class": receipt.provider,
            "source_ref": receipt.source_ref,
            "metadata": DemoRun._receipt_metadata(receipt),
        }

    @staticmethod
    def _receipt_metadata(receipt: AgentExecutionReceipt) -> dict[str, Any]:
        return {
            "provider": receipt.provider,
            "model": receipt.model,
            "elapsed_us": receipt.elapsed_us,
            "model_calls": receipt.model_calls,
            "input_tokens": receipt.input_tokens,
            "output_tokens": receipt.output_tokens,
            "total_tokens": receipt.total_tokens,
            "event_authors": list(receipt.event_authors),
        }

    @staticmethod
    def _public_receipt(receipt: AgentExecutionReceipt) -> dict[str, Any]:
        return {
            "checkpoint_id": receipt.checkpoint_id,
            "agent_id": receipt.agent_id,
            "provider": receipt.provider,
            "model": receipt.model,
            "elapsed_us": receipt.elapsed_us,
            "model_calls": receipt.model_calls,
            "input_tokens": receipt.input_tokens,
            "output_tokens": receipt.output_tokens,
            "total_tokens": receipt.total_tokens,
            "invocation_ids": list(receipt.invocation_ids),
            "event_authors": list(receipt.event_authors),
        }

    def _record(
        self,
        event_type: EventType,
        message: str,
        *,
        checkpoint_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._event_seq += 1
        self.events.append(
            FlightEvent(
                event_id=self._event_seq,
                run_id=self.run_id,
                event_type=event_type,
                checkpoint_id=checkpoint_id,
                message=message,
                data=data or {},
            )
        )


def _aggregate_usage(receipts: Iterable[AgentExecutionReceipt]) -> dict[str, int | None]:
    items = list(receipts)
    if not items:
        return {"model_calls": None, "input_tokens": None, "output_tokens": None}

    def total(field: str) -> int | None:
        values = [getattr(item, field) for item in items]
        if any(value is None for value in values):
            return None
        return sum(int(value) for value in values if value is not None)

    return {
        "model_calls": total("model_calls"),
        "input_tokens": total("input_tokens"),
        "output_tokens": total("output_tokens"),
    }
