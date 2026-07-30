#!/usr/bin/env python3
"""
Topological sorting with lexicographically smallest order.
"""

import heapq
from collections import defaultdict, deque
from typing import List, Tuple, Optional

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    Return a topological ordering of the graph defined by `edges`.
    If multiple orderings exist, return the lexicographically smallest one.
    If the graph contains a cycle (including self-loops), return None.

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
    # Build graph and indegree dictionary
    adj = defaultdict(set)          # use set to avoid duplicate edges affecting indegree
    indeg = defaultdict(int)

    all_nodes = set()

    # Process edges
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1
        all_nodes.add(a)
        all_nodes.add(b)

    # Add optional nodes
    if nodes:
        for n in nodes:
            all_nodes.add(n)
            # Ensure node exists in dicts to avoid KeyError later
            indeg.setdefault(n, 0)
            adj.setdefault(n, set())

    # Initialize min-heap with nodes having zero indegree
    heap = [node for node in all_nodes if indeg.get(node, 0) == 0]
    heapq.heapify(heap)

    result = []
    processed_count = 0

    while heap:
        cur = heapq.heappop(heap)
        result.append(cur)
        processed_count += 1
        for nxt in sorted(adj[cur]):  # sorting to maintain deterministic order when popping from set
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(heap, nxt)

    if processed_count != len(all_nodes):
        return None  # cycle detected

    return result
