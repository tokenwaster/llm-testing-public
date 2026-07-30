#!/usr/bin/env python3
"""
topo_sort implementation: topological sorting with lexicographically smallest order.
"""

from __future__ import annotations

import heapq
from collections import defaultdict
from typing import List, Optional, Tuple


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the graph defined by `edges`.
    If the graph contains a cycle (including self-loops), return None.

    Parameters
    ----------
    edges : List[Tuple[str, str]]
        Each tuple (a, b) indicates that node 'a' must come before node 'b'.
    nodes : Optional[List[str]] = None
        Additional nodes to include in the ordering even if they have no edges.
        Nodes appearing in `edges` are always included.

    Returns
    -------
    List[str] | None
        The topological order or None if a cycle exists.
    """
    # Build adjacency list and indegree map, ignoring duplicate edges
    adj: defaultdict[str, set[str]] = defaultdict(set)
    indeg: dict[str, int] = defaultdict(int)

    all_nodes_set = set()

    for u, v in edges:
        all_nodes_set.update([u, v])
        # Self-loop is a cycle
        if u == v:
            return None
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1

    if nodes:
        all_nodes_set.update(nodes)

    # Ensure every node appears in indegree map
    for n in all_nodes_set:
        indeg.setdefault(n, 0)

    # Initialize min-heap with nodes having zero indegree
    heap = [n for n in indeg if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        for neigh in adj.get(node, ()):
            indeg[neigh] -= 1
            if indeg[neigh] == 0:
                heapq.heappush(heap, neigh)

    # If all nodes processed, return result; else cycle detected
    if len(result) == len(all_nodes_set):
        return result
    return None


# Example usage (uncomment to test)
if __name__ == "__main__":
    print(topo_sort([("b", "c"), ("a", "c")]))  # ["a", "b", "c"]
