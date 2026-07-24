from __future__ import annotations

import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    adj = defaultdict(list)
    in_degree = defaultdict(int)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if a == b:
            return None
        adj[a].append(b)
        in_degree[b] += 1

    if nodes:
        all_nodes.update(nodes)

    heap: list[str] = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None
    return result
