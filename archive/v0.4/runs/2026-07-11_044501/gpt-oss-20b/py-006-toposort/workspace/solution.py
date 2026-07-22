#!/usr/bin/env python3
"""
topo_sort implementation: returns lexicographically smallest topological ordering or None on cycle.
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
    Perform a topological sort on a directed graph defined by `edges`.

    Parameters
    ----------
    edges : list of (str, str)
        Each tuple (a, b) indicates that node `a` must come before node `b`.
    nodes : list of str, optional
        Additional nodes to include in the output even if they have no edges.
        Nodes mentioned in `edges` are always included.

    Returns
    -------
    list[str] or None
        Lexicographically smallest topological ordering of all nodes,
        or ``None`` if a cycle exists (including self-loops).
    """
    # Build adjacency list and indegree map
    adj = defaultdict(set)  # use set to ignore duplicate edges
    indeg = defaultdict(int)

    # Collect all nodes from edges
    for u, v in edges:
        if u == v:  # self-loop => cycle
            return None
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1

    # Include any nodes that appear only as sources with no outgoing edges
    all_nodes = set(indeg.keys()) | set(adj.keys())
    if nodes:
        all_nodes.update(nodes)

    # Ensure every node has an entry in indegree map
    for n in all_nodes:
        indeg.setdefault(n, 0)

    # Initialize min-heap with nodes of zero indegree
    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj.get(u, ()):
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)

    # If we processed all nodes, return ordering; else cycle detected
    if len(result) == len(all_nodes):
        return result
    return None


# Example usage and simple tests
if __name__ == "__main__":
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]
    assert topo_sort([("a", "b"), ("b", "c")], nodes=["d"]) == ["a", "b", "c", "d"]
    assert topo_sort([("a", "b"), ("b", "a")]) is None
    assert topo_sort([("x", "x")]) is None
    print("All tests passed.")
