# solution.py

from __future__ import annotations

import heapq
from collections import defaultdict
from typing import List, Tuple, Optional


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: List[str] | None = None,
) -> List[str] | None:
    """
    Return a lexicographically smallest topological ordering of the directed graph
    defined by ``edges`` (each a pair (a, b) meaning *a* must precede *b*).

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Directed edges of the graph. May contain duplicates or self‑loops.
    nodes : list[str] | None, optional
        Additional isolated nodes that must appear in the output. If omitted,
        only nodes appearing in ``edges`` are considered.

    Returns
    -------
    list[str] | None
        A topological ordering respecting all constraints, chosen lexicographically
        smallest at each step (Kahn's algorithm with a min‑heap). Returns ``None``
        when the graph contains a cycle (including any self‑loop).

    Examples
    --------
    >>> topo_sort([("b", "c"), ("a", "c")])
    ['a', 'b', 'c']
    """
    # Gather all distinct nodes
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    if nodes is not None:
        all_nodes.update(nodes)

    # Early detection of self‑loops which are cycles by definition
    for a, b in edges:
        if a == b:
            return None

    # Build adjacency list with deduplication and compute indegrees
    adj: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = {node: 0 for node in all_nodes}

    for a, b in edges:
        if b not in adj[a]:               # ignore duplicate edges
            adj[a].add(b)
            indegree[b] += 1

    # Min‑heap of nodes with zero indegree
    heap: List[str] = [node for node, deg in indegree.items() if deg == 0]
    heapq.heapify(heap)

    result: List[str] = []

    while heap:
        cur = heapq.heappop(heap)
        result.append(cur)

        for nxt in sorted(adj.get(cur, [])):  # sorting not strictly needed, but keeps deterministic order
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    # If we processed every node, we have a valid ordering
    if len(result) == len(all_nodes):
        return result
    return None
