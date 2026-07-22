from __future__ import annotations

import heapq


def topo_sort(
    edges: list[tuple[str, str]],
    nodes: list[str] | None = None,
) -> list[str] | None:
    graph: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    def add_node(node: str) -> None:
        if node not in graph:
            graph[node] = set()
            indegree[node] = 0

    if nodes is not None:
        for node in nodes:
            add_node(node)

    for a, b in edges:
        add_node(a)
        add_node(b)
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    available = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(available)

    result: list[str] = []

    while available:
        node = heapq.heappop(available)
        result.append(node)

        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    return result if len(result) == len(graph) else None
