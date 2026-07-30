import heapq
from typing import Optional


def topo_sort(
    edges: list[tuple[str, str]],
    nodes: Optional[list[str]] = None,
) -> Optional[list[str]]:
    all_nodes: set[str] = set(nodes) if nodes else set()

    adjacency: dict[str, list[str]] = {}
    indegree: dict[str, int] = {}

    for node in all_nodes:
        adjacency[node] = []
        indegree[node] = 0

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

        adjacency.setdefault(a, [])
        adjacency.setdefault(b, [])
        indegree.setdefault(a, 0)
        indegree.setdefault(b, 0)

        adjacency[a].append(b)
        indegree[b] += 1

    heap = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in adjacency.get(current, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
