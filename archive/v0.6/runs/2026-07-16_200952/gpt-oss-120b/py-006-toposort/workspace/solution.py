# solution.py
from __future__ import annotations

import heapq
from collections import defaultdict
from typing import List, Tuple, Optional, Set


def topo_sort(
    edges: List[Tuple[str, str]],
    nodes: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Return a lexicographically smallest topological ordering of the given graph.

    Parameters
    ----------
    edges : list[tuple[str, str]]
        Each tuple (a, b) means ``a`` must appear before ``b``.
    nodes : list[str] | None, optional
        Additional nodes that must appear in the output even if they have no
        incident edges. Nodes that appear in ``edges`` are always included.

    Returns
    -------
    list[str] | None
        A topological ordering of all nodes, or ``None`` if the graph contains a
        cycle (including a self‑loop).

    Notes
    -----
    The algorithm is Kahn's topological sort using a min‑heap to guarantee the
    lexicographically smallest possible ordering at each step.
    """
    # ------------------------------------------------------------------ #
    # 1. Gather all distinct nodes and detect immediate self‑loops.
    # ------------------------------------------------------------------ #
    all_nodes: Set[str] = set()
    edge_set: Set[Tuple[str, str]] = set()
    for a, b in edges:
        if a == b:               # self‑loop => cycle
            return None
        edge_set.add((a, b))
        all_nodes.add(a)
        all_nodes.add(b)

    if nodes:
        all_nodes.update(nodes)

    # ------------------------------------------------------------------ #
    # 2. Build adjacency list and indegree map.
    # ------------------------------------------------------------------ #
    adj: defaultdict[str, List[str]] = defaultdict(list)
    indegree: dict[str, int] = {node: 0 for node in all_nodes}

    for a, b in edge_set:
        adj[a].append(b)
        indegree[b] += 1

    # ------------------------------------------------------------------ #
    # 3. Initialise min‑heap with all nodes of indegree 0.
    # ------------------------------------------------------------------ #
    heap: List[str] = [node for node, deg in indegree.items() if deg == 0]
    heapq.heapify(heap)

    result: List[str] = []

    # ------------------------------------------------------------------ #
    # 4. Process nodes.
    # ------------------------------------------------------------------ #
    while heap:
        cur = heapq.heappop(heap)
        result.append(cur)

        for nxt in adj.get(cur, []):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    # ------------------------------------------------------------------ #
    # 5. Detect cycle.
    # ------------------------------------------------------------------ #
    if len(result) != len(all_nodes):
        return None

    return result
