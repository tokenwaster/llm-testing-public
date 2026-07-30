#!/usr/bin/env python3
"""
topo_sort implementation with lexicographically smallest topological ordering.
"""

from __future__ import annotations

import heapq
from collections import defaultdict, deque
from typing import List, Tuple, Optional


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: List[str] | None = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the graph defined by `edges`.
    If a cycle exists (including self-loops), return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Each tuple (a, b) means node 'a' must come before node 'b'.
    nodes : list[str] | None, optional
        Additional nodes that should appear in the output even if they have no edges.
        Nodes appearing in `edges` are always included.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if a cycle exists.
    """
    # Build adjacency set to avoid duplicate edges affecting indegree counts
    adj: defaultdict[set[str]] = defaultdict(set)
    indeg: defaultdict[int] = defaultdict(int)

    all_nodes_set = set()

    for u, v in edges:
        if u == v:
            # Self-loop is a cycle
            return None
        all_nodes_set.update([u, v])
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1

    # Include any nodes that appear only as sources with no outgoing edges
    for u in list(adj.keys()):
        all_nodes_set.add(u)

    # Add optional nodes
    if nodes:
        all_nodes_set.update(nodes)

    # Ensure every node has an entry in indegree dict
    for n in all_nodes_set:
        indeg.setdefault(n, 0)

    # Initialize min-heap with nodes of zero indegree
    heap: List[str] = [n for n in all_nodes_set if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        # Decrease indegree of neighbors
        for neigh in adj.get(node, ()):
            indeg[neigh] -= 1
            if indeg[neigh] == 0:
                heapq.heappush(heap, neigh)

    if len(result) != len(all_nodes_set):
        # Cycle detected
        return None

    return result


# Example usage and simple test cases
if __name__ == "__main__":
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]
    assert topo_sort([("a", "b"), ("b", "c")]) == ["a", "b", "c"]
    # Lexicographic tie
    assert topo_sort([("a", "c"), ("b", "c")]) == ["a", "b", "c"]
    # Additional nodes with no edges
    assert topo_sort([], ["x", "y"]) == ["x", "y"]
    # Cycle detection
    assert topo_sort([("a", "b"), ("b", "a")]) is None
    # Self-loop
    assert topo_sort([("a", "a")]) is None

    print("All tests passed.")
