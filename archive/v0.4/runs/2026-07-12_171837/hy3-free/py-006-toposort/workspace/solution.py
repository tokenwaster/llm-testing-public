from __future__ import annotations

import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        all_nodes.update(nodes)

    adj = {node: [] for node in all_nodes}
    indegree = {node: 0 for node in all_nodes}

    for a, b in edges:
        adj[a].append(b)
        indegree[b] += 1

    heap = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nb in adj[node]:
            indegree[nb] -= 1
            if indegree[nb] == 0:
                heapq.heappush(heap, nb)

    if len(result) != len(all_nodes):
        return None
    return result
