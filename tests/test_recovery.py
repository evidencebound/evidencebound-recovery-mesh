from __future__ import annotations

from recovery_mesh.graph import TrustGraph
from recovery_mesh.models import TrustBreak, TrustBreakClass, TrustStatus
from recovery_mesh.recovery import RecoveryEngine, RecoveryInvariantError, SideEffectLedger
from recovery_mesh.workload import RUN_ID, build_demo_checkpoints


def _break(
    checkpoint_id: str, break_class: TrustBreakClass = TrustBreakClass.EVIDENCE
) -> TrustBreak:
    return TrustBreak(
        break_id=f"break:{checkpoint_id}",
        run_id=RUN_ID,
        checkpoint_id=checkpoint_id,
        break_class=break_class,
        reason_code="CONTROLLED_TEST",
        reason="controlled test trust break",
        controlled=True,
    )


def test_exact_blast_radius_reuses_unaffected_scout_branch() -> None:
    engine = RecoveryEngine(TrustGraph(build_demo_checkpoints()))
    plan = engine.plan(_break("history_snapshot"))
    assert plan.blast_radius.invalidated_source == "history_snapshot"
    assert plan.blast_radius.contaminated_checkpoints == (
        "statistician",
        "skeptic",
        "orchestrator",
        "publish_action",
    )
    assert plan.blast_radius.recomputation_set == (
        "history_snapshot",
        "statistician",
        "skeptic",
        "orchestrator",
    )
    assert plan.blast_radius.blocked_action_nodes == ("publish_action",)
    assert set(plan.blast_radius.reusable_checkpoints) == {
        "fixture_snapshot",
        "policy_rules",
        "scout",
    }


def test_apply_plan_marks_source_descendants_and_action() -> None:
    engine = RecoveryEngine(TrustGraph(build_demo_checkpoints()))
    plan = engine.plan(_break("history_snapshot"))
    graph = engine.apply_plan(plan)
    assert graph.checkpoint("history_snapshot").verification_status is TrustStatus.INVALIDATED
    assert graph.checkpoint("statistician").verification_status is TrustStatus.RECOMPUTE
    assert graph.checkpoint("scout").verification_status is TrustStatus.VERIFIED
    assert graph.checkpoint("publish_action").verification_status is TrustStatus.BLOCKED


def test_recovery_requires_topological_dependency_verification() -> None:
    engine = RecoveryEngine(TrustGraph(build_demo_checkpoints()))
    engine.apply_plan(engine.plan(_break("history_snapshot")))
    try:
        engine.verify_recomputed("statistician", structured_output={"claim": "too early"})
    except RecoveryInvariantError as exc:
        assert "history_snapshot is not VERIFIED" in str(exc)
    else:
        raise AssertionError("expected fail-closed dependency gate")

    engine.verify_recomputed("history_snapshot", structured_output={"sample_size": 20})
    stat = engine.verify_recomputed(
        "statistician",
        structured_output={"claim": "recomputed", "evidence_ids": ["history"], "confidence": 0.61},
    )
    assert stat.verification_status is TrustStatus.VERIFIED


def test_full_selective_recovery_unblocks_action_and_suppresses_duplicate_side_effect() -> None:
    engine = RecoveryEngine(TrustGraph(build_demo_checkpoints()))
    engine.apply_plan(engine.plan(_break("history_snapshot")))
    ledger = SideEffectLedger()

    try:
        engine.resume_action("publish_action", payload={"verdict": "safe"}, ledger=ledger)
    except RecoveryInvariantError as exc:
        assert "remains BLOCKED" in str(exc)
    else:
        raise AssertionError("unsafe action was not blocked")

    engine.verify_recomputed("history_snapshot", structured_output={"sample_size": 20})
    engine.verify_recomputed("statistician", structured_output={"claim": "stat-v2"})
    engine.verify_recomputed("skeptic", structured_output={"claim": "skeptic-v2"})
    engine.verify_recomputed("orchestrator", structured_output={"claim": "orchestrator-v2"})

    first = engine.resume_action("publish_action", payload={"verdict": "safe"}, ledger=ledger)
    second = engine.resume_action("publish_action", payload={"verdict": "safe"}, ledger=ledger)
    assert not first.duplicate_suppressed
    assert second.duplicate_suppressed
    assert first.payload_digest == second.payload_digest
    assert engine.graph.checkpoint("publish_action").verification_status is TrustStatus.VERIFIED


def test_idempotency_key_rejects_conflicting_replay() -> None:
    ledger = SideEffectLedger()
    ledger.commit("key", {"v": 1})
    try:
        ledger.commit("key", {"v": 2})
    except RecoveryInvariantError as exc:
        assert "different payload" in str(exc)
    else:
        raise AssertionError("conflicting replay must fail")
