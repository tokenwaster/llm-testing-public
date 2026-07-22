#!/usr/bin/env python3
"""
topo_sort implementation.
"""

from __future__ import annotations

import heapq
from collections import defaultdict, deque
from typing import Iterable, List, Optional, Tuple


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the graph defined by `edges`.
    If a cycle exists (including self-loops), return None.

    Parameters
    ----------
    edges : List[Tuple[str, str]]
        Each tuple (a, b) indicates that node 'a' must come before node 'b'.
    nodes : Optional[List[str]] = None
        Additional nodes to include in the ordering even if they have no edges.
        Nodes mentioned in `edges` are always included.

    Returns
    -------
    Optional[List[str]]
        Lexicographically smallest topological order or None if a cycle exists.
    """
    # Build adjacency list and indegree map, ignoring duplicate edges
    adj: defaultdict[str, set[str]] = defaultdict(set)
    indeg: defaultdict[int] = defaultdict(int)

    all_nodes_set = set()

    for u, v in edges:
        # Self-loop is an immediate cycle
        if u == v:
            return None

        all_nodes_set.update([u, v])

        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1
            # Ensure nodes with no outgoing edges are present in indeg dict
            indeg.setdefault(u, indeg.get(u, 0))

    # Include any extra nodes provided by the caller
    if nodes:
        for n in nodes:
            all_nodes_set.add(n)
            indeg.setdefault(n, indeg.get(n, 0))
            adj.setdefault(n, set())

    # Initialize min-heap with nodes of zero indegree
    heap: List[str] = [node for node in all_nodes_set if indeg[node] == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        cur = heapq.heappop(heap)
        result.append(cur)

        for nxt in sorted(adj[cur]):  # sorting to maintain deterministic order
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(heap, nxt)

    # If we processed all nodes, return the ordering; otherwise a cycle exists
    if len(result) == len(all_nodes_set):
        return result
    else:
        return None


# Example usage (uncomment to test)
if __name__ == "__main__":
    print(topo_sort([("b", "c"), ("a", "c")]))
