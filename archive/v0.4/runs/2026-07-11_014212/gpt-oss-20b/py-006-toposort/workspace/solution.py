#!/usr/bin/env python3
"""
topo_sort implementation.
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
    If the graph contains a cycle, return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        List of directed edges (a, b) meaning a must come before b.
    nodes : list[str] | None
        Optional list of additional nodes that should appear in the output even if they have no edges.

    Returns
    -------
    list[str] | None
        Lexicographically smallest topological ordering or None if a cycle exists.
    """
    # Build adjacency list and indegree map
    adj = defaultdict(set)  # use set to ignore duplicate edges
    indeg = defaultdict(int)

    all_nodes_set = set()

    for a, b in edges:
        all_nodes_set.update([a, b])
        if a == b:  # self-loop => cycle
            return None
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

    if nodes is not None:
        all_nodes_set.update(nodes)

    # Ensure every node appears in indegree map
    for n in all_nodes_set:
        indeg.setdefault(n, 0)

    # Initialize min-heap with zero-indegree nodes
    heap = [n for n in indeg if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neigh in adj[node]:
            indeg[neigh] -= 1
            if indeg[neigh] == 0:
                heapq.heappush(heap, neigh)

    # If all nodes processed, return result; otherwise cycle detected
    if len(result) == len(all_nodes_set):
        return result
    return None


# Example usage (uncomment to test)
if __name__ == "__main__":
    print(topo_sort([("b", "c"), ("a", "c")]))  # ["a", "b", "c"]
