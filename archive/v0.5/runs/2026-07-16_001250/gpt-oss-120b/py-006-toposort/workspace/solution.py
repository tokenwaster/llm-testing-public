# solution.py
from __future__ import annotations

import heapq
from collections import defaultdict
from typing import List, Tuple, Optional


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the directed graph.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Each tuple (a, b) means an edge a → b (a must appear before b).
    nodes : list[str] | None, optional
        Additional nodes that must appear in the output even if they have no incident
        edges. Nodes that appear in ``edges`` are always included.

    Returns
    -------
    list[str] | None
        A topological ordering of all nodes, choosing the alphabetically first
        available node at each step. If the graph contains a cycle (including a
        self‑loop), ``None`` is returned.
    """
    # Build the set of all nodes
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    # Adjacency list without duplicate edges
    adj: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = {node: 0 for node in all_nodes}

    # Process edges, detect self‑loops early
    for a, b in edges:
        if a == b:
            # Self‑loop => cycle
            return None
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    # Min‑heap of nodes with indegree 0
    heap: List[str] = [node for node, deg in indegree.items() if deg == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neigh in sorted(adj.get(node, [])):
            indegree[neigh] -= 1
            if indegree[neigh] == 0:
                heapq.heappush(heap, neigh)

    # If we processed all nodes, we have a valid ordering
    if len(result) == len(all_nodes):
        return result
    # Otherwise a cycle exists
    return None
