#!/usr/bin/env python3
"""
Topological sort with lexicographically smallest ordering.
"""

from __future__ import annotations

import heapq
from collections import defaultdict
from typing import List, Tuple, Optional


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: List[str] | None = None,
) -> Optional[List[str]]:
    """
    Return a topological ordering of the graph defined by `edges`.
    If multiple orderings exist, return the lexicographically smallest one.
    If the graph contains a cycle (including self‑loops), return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        List of directed edges (a, b) meaning a must come before b.
    nodes : list[str] | None, optional
        Additional nodes that should appear in the output even if they have no edges.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if a cycle exists.
    """
    # Build adjacency set and indegree dict
    adj: defaultdict[str, set[str]] = defaultdict(set)
    indeg: defaultdict[int, int] = defaultdict(int)

    all_nodes = set(nodes) if nodes else set()

    for a, b in edges:
        if a == b:
            # Self-loop is a cycle
            return None
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1
        # Ensure nodes are known even if they only appear as targets
        all_nodes.update([a, b])

    # Add any extra nodes that were explicitly provided
    if nodes:
        all_nodes.update(nodes)

    # Initialize min-heap with nodes of zero indegree
    heap: List[str] = [node for node in all_nodes if indeg[node] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in sorted(adj[u]):  # sorting ensures deterministic order
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)

    if len(result) != len(all_nodes):
        # Cycle detected (some nodes never reached zero indegree)
        return None

    return result


# Example usage and simple tests
if __name__ == "__main__":
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]
    assert topo_sort([("a", "b"), ("b", "c")]) == ["a", "b", "c"]
    # Lexicographic tie
    assert topo_sort([("a", "c"), ("b", "c")]) == ["a", "b", "c"]
    # Self-loop
    assert topo_sort([("x", "x")]) is None
    # Cycle
    assert topo_sort([("a", "b"), ("b", "a")]) is None
    # Extra nodes
    assert topo_sort([], nodes=["z"]) == ["z"]
    print("All tests passed.")
