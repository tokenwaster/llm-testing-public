#!/usr/bin/env python3
"""
topo_sort implementation with lexicographically smallest ordering.
"""

from __future__ import annotations

import heapq
from collections import defaultdict, deque
from typing import List, Optional, Tuple


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: List[str] | None = None,
) -> List[str] | None:
    """
    Return a topological ordering of the graph defined by `edges`.
    If multiple orderings exist, return the lexicographically smallest one.
    If the graph contains a cycle, return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Each tuple (a, b) means a must come before b.
    nodes : list[str] | None, optional
        Additional nodes that should appear in the output even if they have no edges.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if a cycle exists.
    """
    # Build adjacency list and indegree counts
    adj = defaultdict(set)  # type: dict[str, set[str]]
    indeg = defaultdict(int)  # type: dict[str, int]
    all_nodes = set()

    for u, v in edges:
        all_nodes.update([u, v])
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1
            # Ensure nodes with no outgoing edges are present in indeg dict
            indeg.setdefault(u, indeg.get(u, 0))

    if nodes:
        all_nodes.update(nodes)

    # Ensure every node appears in indegree dictionary
    for n in all_nodes:
        indeg.setdefault(n, 0)

    # Initialize min-heap with nodes having zero indegree
    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        # For each neighbor, reduce indegree and push to heap if zero
        for neigh in sorted(adj.get(node, [])):
            indeg[neigh] -= 1
            if indeg[neigh] == 0:
                heapq.heappush(heap, neigh)

    # If result contains all nodes, success; otherwise cycle detected
    return result if len(result) == len(all_nodes) else None


# Example usage and simple tests
if __name__ == "__main__":
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]
    assert topo_sort([("a", "b"), ("b", "c")]) == ["a", "b", "c"]
    # Lexicographic tie
    assert topo_sort([("a", "c"), ("b", "c")]) == ["a", "b", "c"]
    # Cycle detection
    assert topo_sort([("a", "b"), ("b", "a")]) is None
    # Self-loop cycle
    assert topo_sort([("x", "x")]) is None
    # Additional nodes with no edges
    assert topo_sort([], ["z", "y"]) == ["y", "z"]
    print("All tests passed.")
