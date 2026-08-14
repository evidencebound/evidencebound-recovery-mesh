from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from .models import Checkpoint


class GraphInvariantError(ValueError):
    pass


class TrustGraph:
    """Directed acyclic graph where edges point dependency -> dependent checkpoint."""

    def __init__(self, checkpoints: Iterable[Checkpoint]):
        items = list(checkpoints)
        self._nodes = {item.checkpoint_id: item for item in items}
        if len(self._nodes) != len(items):
            raise GraphInvariantError("duplicate checkpoint_id")
        if not self._nodes:
            raise GraphInvariantError("trust graph cannot be empty")

        run_ids = {item.run_id for item in items}
        if len(run_ids) != 1:
            raise GraphInvariantError("all checkpoints must belong to one run")
        self.run_id = next(iter(run_ids))

        self._children: dict[str, set[str]] = defaultdict(set)
        self._parents: dict[str, set[str]] = defaultdict(set)
        for item in items:
            for parent in item.dependency_checkpoint_ids:
                if parent not in self._nodes:
                    raise GraphInvariantError(
                        f"checkpoint {item.checkpoint_id} references unknown dependency {parent}"
                    )
                if parent == item.checkpoint_id:
                    raise GraphInvariantError("checkpoint cannot depend on itself")
                self._children[parent].add(item.checkpoint_id)
                self._parents[item.checkpoint_id].add(parent)

        self._topological = self._topological_sort()

    @property
    def checkpoints(self) -> tuple[Checkpoint, ...]:
        return tuple(self._nodes[item] for item in self._topological)

    def checkpoint(self, checkpoint_id: str) -> Checkpoint:
        try:
            return self._nodes[checkpoint_id]
        except KeyError as exc:
            raise KeyError(f"unknown checkpoint_id: {checkpoint_id}") from exc

    def parents(self, checkpoint_id: str) -> frozenset[str]:
        self.checkpoint(checkpoint_id)
        return frozenset(self._parents[checkpoint_id])

    def children(self, checkpoint_id: str) -> frozenset[str]:
        self.checkpoint(checkpoint_id)
        return frozenset(self._children[checkpoint_id])

    def descendants(self, checkpoint_id: str) -> frozenset[str]:
        self.checkpoint(checkpoint_id)
        seen: set[str] = set()
        queue = deque(self._children[checkpoint_id])
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(self._children[current])
        return frozenset(seen)

    def ancestors(self, checkpoint_id: str) -> frozenset[str]:
        self.checkpoint(checkpoint_id)
        seen: set[str] = set()
        queue = deque(self._parents[checkpoint_id])
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(self._parents[current])
        return frozenset(seen)

    def topological_subset(self, checkpoint_ids: Iterable[str]) -> tuple[str, ...]:
        requested = set(checkpoint_ids)
        unknown = requested.difference(self._nodes)
        if unknown:
            raise KeyError(f"unknown checkpoint ids: {sorted(unknown)}")
        return tuple(item for item in self._topological if item in requested)

    def replace(self, checkpoint: Checkpoint) -> TrustGraph:
        if checkpoint.checkpoint_id not in self._nodes:
            raise KeyError(f"unknown checkpoint_id: {checkpoint.checkpoint_id}")
        if checkpoint.run_id != self.run_id:
            raise GraphInvariantError("replacement run_id mismatch")
        items = [
            checkpoint if current.checkpoint_id == checkpoint.checkpoint_id else current
            for current in self.checkpoints
        ]
        return TrustGraph(items)

    def replace_many(self, replacements: Iterable[Checkpoint]) -> TrustGraph:
        by_id = {item.checkpoint_id: item for item in replacements}
        unknown = set(by_id).difference(self._nodes)
        if unknown:
            raise KeyError(f"unknown checkpoint ids: {sorted(unknown)}")
        items = [by_id.get(current.checkpoint_id, current) for current in self.checkpoints]
        return TrustGraph(items)

    def _topological_sort(self) -> tuple[str, ...]:
        indegree = {item: len(self._parents[item]) for item in self._nodes}
        queue = deque(sorted(item for item, degree in indegree.items() if degree == 0))
        ordered: list[str] = []
        while queue:
            current = queue.popleft()
            ordered.append(current)
            for child in sorted(self._children[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if len(ordered) != len(self._nodes):
            raise GraphInvariantError("trust graph must be acyclic")
        return tuple(ordered)
