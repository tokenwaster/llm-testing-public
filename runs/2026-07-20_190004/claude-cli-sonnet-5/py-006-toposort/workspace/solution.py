import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes or [])
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj = defaultdict(set)
    in_degree = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            in_degree[b] += 1

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result = []
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
