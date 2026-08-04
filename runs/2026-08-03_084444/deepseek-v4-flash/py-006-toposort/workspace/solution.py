from __future__ import annotations

import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = defaultdict(int)
    all_nodes: set[str] = set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    if nodes is not None:
        all_nodes.update(nodes)

    for node in all_nodes:
        indegree.setdefault(node, 0)

    heap = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        for neighbor in graph.get(node, ()):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
