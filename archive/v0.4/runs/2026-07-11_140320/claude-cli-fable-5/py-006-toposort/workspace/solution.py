import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes or [])
    adj = defaultdict(set)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adj[a].add(b)

    indegree = {n: 0 for n in all_nodes}
    for a, targets in adj.items():
        for b in targets:
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    order = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for m in adj[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(order) != len(all_nodes):
        return None
    return order
