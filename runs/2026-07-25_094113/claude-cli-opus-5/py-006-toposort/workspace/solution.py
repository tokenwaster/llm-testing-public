import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes: set[str] = set(nodes or [])
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    successors: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b in successors[a]:
            continue
        successors[a].add(b)
        indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for nxt in successors[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(order) != len(all_nodes):
        return None
    return order
