from __future__ import annotations

from datetime import UTC, datetime

import pytest

from recovery_mesh.graph import GraphInvariantError, TrustGraph
from recovery_mesh.hashing import sha256_digest
from recovery_mesh.models import (
    Checkpoint,
    CheckpointKind,
    IntegrityMetadata,
    ProvenanceMetadata,
)
from recovery_mesh.workload import build_demo_checkpoints


def test_demo_graph_topology_and_dependencies() -> None:
    graph = TrustGraph(build_demo_checkpoints())
    assert graph.descendants("history_snapshot") == frozenset(
        {"statistician", "skeptic", "orchestrator", "publish_action"}
    )
    assert graph.ancestors("orchestrator") == frozenset(
        {"fixture_snapshot", "history_snapshot", "policy_rules", "statistician", "scout", "skeptic"}
    )
    order = graph.topological_subset({"statistician", "skeptic", "orchestrator"})
    assert order == ("statistician", "skeptic", "orchestrator")


def test_unknown_dependency_is_rejected() -> None:
    digest = sha256_digest({"x": 1})
    checkpoint = Checkpoint(
        run_id="r",
        checkpoint_id="a",
        kind=CheckpointKind.EVIDENCE,
        dependency_checkpoint_ids=("missing",),
        policy_version="p",
        structured_output_digest=digest,
        integrity=IntegrityMetadata(digest=digest),
        provenance=ProvenanceMetadata(source_class="test"),
        created_at=datetime.now(UTC),
    )
    with pytest.raises(GraphInvariantError, match="unknown dependency"):
        TrustGraph([checkpoint])


def test_cycle_is_rejected() -> None:
    base = build_demo_checkpoints()[0]
    digest = base.structured_output_digest
    a = base.model_copy(
        update={"run_id": "r", "checkpoint_id": "a", "dependency_checkpoint_ids": ("b",)}
    )
    b = base.model_copy(
        update={"run_id": "r", "checkpoint_id": "b", "dependency_checkpoint_ids": ("a",)}
    )
    assert a.integrity.digest == digest
    with pytest.raises(GraphInvariantError, match="acyclic"):
        TrustGraph([a, b])
