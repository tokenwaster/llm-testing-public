import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj = defaultdict(set)
    indegree = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
