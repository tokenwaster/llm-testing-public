import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph: dict[str, list[str]] = defaultdict(list)
    all_nodes: set[str] = set()

    if nodes is not None:
        all_nodes.update(nodes)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        graph[a].append(b)

    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    for a, b in edges:
        in_degree[b] += 1

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None
    return result
