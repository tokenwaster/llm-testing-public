#!/usr/bin/env python3
"""
topo_sort implementation using Kahn's algorithm with a min‑heap to produce the lexicographically smallest topological ordering.
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
    If a cycle exists (including self‑loops), return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        List of directed edges (a, b) meaning a must come before b.
    nodes : list[str] | None, optional
        Additional nodes that should appear in the output even if they have no edges.
        Nodes mentioned in `edges` are always included.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if a cycle exists.
    """
    # Build adjacency list and indegree map
    adj = defaultdict(set)  # use set to avoid duplicate edges
    indeg = defaultdict(int)

    all_nodes_set = set()

    for a, b in edges:
        # self-loop is a cycle
        if a == b:
            return None

        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

        all_nodes_set.update([a, b])

    # Add nodes from the optional list
    if nodes:
        for n in nodes:
            all_nodes_set.add(n)

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

        for neigh in adj.get(node, []):
            indeg[neigh] -= 1
            if indeg[neigh] == 0:
                heapq.heappush(heap, neigh)

    # If all nodes processed, return ordering; else cycle detected
    if len(result) == len(all_nodes_set):
        return result
    return None


# Example usage (uncomment to test)
if __name__ == "__main__":
    print(topo_sort([("b", "c"), ("a", "c")]))  # ["a", "b", "c"]
