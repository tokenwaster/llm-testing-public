#!/usr/bin/env python3
"""
topo_sort implementation using Kahn's algorithm with a min-heap.
"""

from __future__ import annotations

import heapq
from collections import defaultdict, deque
from typing import List, Tuple, Optional


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the graph defined by `edges`.
    If a cycle exists, return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        List of directed edges (a, b) meaning a must come before b.
    nodes : list[str] | None, optional
        Additional nodes that should appear in the output even if they have no edges.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if graph has a cycle.
    """
    # Build adjacency set and indegree map
    adj = defaultdict(set)  # node -> set of successors
    indeg = defaultdict(int)

    all_nodes_set = set()

    for u, v in edges:
        all_nodes_set.update([u, v])
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1

    if nodes:
        all_nodes_set.update(nodes)

    # Ensure every node appears in indegree map
    for n in all_nodes_set:
        indeg.setdefault(n, 0)

    # Initialize min-heap with zero-indegree nodes
    heap = [n for n in all_nodes_set if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        for succ in adj.get(node, ()):
            indeg[succ] -= 1
            if indeg[succ] == 0:
                heapq.heappush(heap, succ)

    # If all nodes processed, return result; else cycle detected
    if len(result) != len(all_nodes_set):
        return None

    return result


# Example usage and simple tests
if __name__ == "__main__":
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]
    # cycle detection
    assert topo_sort([("a", "b"), ("b", "c"), ("c", "a")]) is None
    # self-loop
    assert topo_sort([("x", "x")]) is None
    # nodes with no edges
    assert topo_sort([], ["z", "y"]) == ["y", "z"]
    print("All tests passed.")
