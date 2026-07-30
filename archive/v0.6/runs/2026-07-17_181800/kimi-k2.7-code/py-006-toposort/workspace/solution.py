from __future__ import annotations
import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """Return the lexicographically smallest topological ordering, or None if a cycle exists."""
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    graph = defaultdict(list)
    indegree = {node: 0 for node in all_nodes}

    for a, b in edges:
        if a == b:
            return None
        graph[a].append(b)
        indegree[b] += 1

    heap = [node for node, deg in indegree.items() if deg == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None
    return result
