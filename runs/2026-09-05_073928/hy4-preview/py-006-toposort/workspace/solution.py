import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adjacency = defaultdict(list)
    indegree: dict[str, int] = {}

    if nodes is not None:
        for node in nodes:
            indegree.setdefault(node, 0)

    for before, after in edges:
        indegree.setdefault(before, 0)
        indegree.setdefault(after, 0)
        adjacency[before].append(after)
        indegree[after] += 1

    heap = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(heap)

    order: list[str] = []

    while heap:
        node = heapq.heappop(heap)
        order.append(node)

        for neighbor in adjacency.get(node, ()):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    return order if len(order) == len(indegree) else None
