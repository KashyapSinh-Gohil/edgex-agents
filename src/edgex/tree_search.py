from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import random


@dataclass
class SearchNode:
    node_id: str
    statement: str
    parent_id: str | None = None
    depth: int = 0
    visits: int = 0
    value: float = 0.0
    status: str = "candidate"

    @property
    def mean_value(self) -> float:
        return self.value / self.visits if self.visits else 0.0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class ResearchTree:
    """AIDE-inspired best-first tree with UCB selection and durable node state."""

    def __init__(self, nodes: list[SearchNode] | None = None, exploration: float = 1.4):
        self.nodes = nodes or []
        self.exploration = exploration

    def add(self, statement: str, parent_id: str | None = None, node_id: str | None = None) -> SearchNode:
        node = SearchNode(
            node_id=node_id or f"node_{len(self.nodes):04d}",
            statement=statement,
            parent_id=parent_id,
            depth=next((n.depth for n in self.nodes if n.node_id == parent_id), -1) + 1,
        )
        self.nodes.append(node)
        return node

    def children(self, parent_id: str | None) -> list[SearchNode]:
        return [n for n in self.nodes if n.parent_id == parent_id]

    def select(self) -> SearchNode | None:
        candidates = [n for n in self.nodes if n.status in {"candidate", "testing"}]
        if not candidates:
            return None
        total_visits = max(1, sum(n.visits for n in self.nodes))
        def ucb(node: SearchNode) -> float:
            if node.visits == 0:
                return float("inf")
            return node.mean_value + self.exploration * math.sqrt(math.log(total_visits) / node.visits)
        return max(candidates, key=ucb)

    def record(self, node_id: str, value: float, status: str = "evaluated") -> None:
        node = next((n for n in self.nodes if n.node_id == node_id), None)
        if node is None:
            raise KeyError(node_id)
        node.visits += 1
        node.value += value
        node.status = status
        parent = node.parent_id
        while parent is not None:
            parent_node = next((n for n in self.nodes if n.node_id == parent), None)
            if parent_node is None:
                break
            parent_node.visits += 1
            parent_node.value += value
            parent = parent_node.parent_id

    def expand_default(self, topic: str, question: str) -> list[SearchNode]:
        """Create independent candidate directions; later model output can replace these."""
        if self.nodes:
            return self.nodes
        root = self.add(f"Define a falsifiable baseline for: {question}")
        self.add(f"Test an algorithmic intervention for: {topic}", parent_id=root.node_id)
        self.add(f"Test a theoretical or mechanistic explanation for: {topic}", parent_id=root.node_id)
        self.add(f"Test a cross-domain transfer or scaling law for: {topic}", parent_id=root.node_id)
        return self.nodes

    def best(self) -> SearchNode | None:
        return max((n for n in self.nodes if n.visits and not self.children(n.node_id)),
                   key=lambda n: n.mean_value, default=None)

    def to_list(self) -> list[dict[str, object]]:
        return [n.as_dict() for n in self.nodes]

    @classmethod
    def from_list(cls, payload: list[dict[str, object]]) -> "ResearchTree":
        return cls([SearchNode(**item) for item in payload])
