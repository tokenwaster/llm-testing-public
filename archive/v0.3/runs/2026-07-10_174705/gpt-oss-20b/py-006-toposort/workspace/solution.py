#!/usr/bin/env python3
"""
topo_sort implementation using Kahn's algorithm with a min-heap to produce the
lexicographically smallest topological ordering.
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
    Return a lexicographically smallest topological ordering of the graph defined by `edges`.
    If a cycle exists, return None.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Each tuple (a, b) indicates that node `a` must come before node `b`.
    nodes : list[str] | None, optional
        Additional nodes to include in the ordering even if they have no edges.
        Nodes mentioned in `edges` are always included.

    Returns
    -------
    list[str] | None
        The topological order or None if a cycle is detected.
    """
    # Build adjacency list and indegree count
    adj = defaultdict(set)  # use set to avoid duplicate edges affecting indegree
    indeg: dict[str, int] = defaultdict(int)

    all_nodes_set = set()

    for u, v in edges:
        if u == v:
            # self-loop creates a cycle immediately
            return None
        adj[u].add(v)
        indeg[v] += 1
        all_nodes_set.update([u, v])

    if nodes:
        all_nodes_set.update(nodes)

    # Ensure every node appears in indegree dict
    for n in all_nodes_set:
        indeg.setdefault(n, 0)

    # Initialize min-heap with nodes of zero indegree
    heap = [n for n in all_nodes_set if indeg[n] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        for neighbor in adj[node]:
            indeg[neighbor] -= 1
            if indeg[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If all nodes processed, return result; otherwise cycle detected
    if len(result) == len(all_nodes_set):
        return result
    return None


# Example usage (uncomment to test)
if __name__ == "__main__":
    print(topo_sort([("b", "c"), ("a", "c")]))  # ["a", "b", "c"]
