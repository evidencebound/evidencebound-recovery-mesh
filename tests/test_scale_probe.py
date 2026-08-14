from __future__ import annotations

from recovery_mesh.graph import TrustGraph
from recovery_mesh.models import CheckpointKind
from recovery_mesh.scale_probe import (
    TOTAL_AGENT_COUNT,
    build_synthetic_100_agent_fleet,
    run_scale_probe,
)


def test_scale_probe_contains_exactly_100_synthetic_agent_checkpoints() -> None:
    graph = TrustGraph(build_synthetic_100_agent_fleet())
    agents = [item for item in graph.checkpoints if item.kind is CheckpointKind.AGENT]
    assert len(agents) == TOTAL_AGENT_COUNT == 100
    assert len(graph.checkpoints) == 110


def test_scale_probe_fault_recomputes_only_one_branch_and_necessary_merges() -> None:
    receipt = run_scale_probe("source_0")
    assert receipt.synthetic_agent_checkpoints == 100
    assert receipt.affected_agent_checkpoints == 14
    assert receipt.reused_agent_checkpoints == 86
    assert receipt.blocked_action_nodes == 1
    assert receipt.affected_agent_ratio == 0.14
    assert receipt.reused_agent_ratio == 0.86
    assert receipt.measurement_class == "deterministic_synthetic_scale_probe"
