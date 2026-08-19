from collections import defaultdict
from heapq import heapify, heappop, heappush


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, set[str]] = defaultdict(set)
    all_nodes: set[str] = set(nodes) if nodes is not None else set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adj[a].add(b)

    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    for a, nbrs in adj.items():
        for b in nbrs:
            if a == b:
                return None
            in_degree[b] += 1

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapify(heap)

    order: list[str] = []
    while heap:
        u = heappop(heap)
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heappush(heap, v)

    if len(order) != len(all_nodes):
        return None
    return order
