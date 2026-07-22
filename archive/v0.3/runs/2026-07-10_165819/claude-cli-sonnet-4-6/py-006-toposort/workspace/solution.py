import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    in_degree = defaultdict(int)
    graph = defaultdict(set)
    all_nodes = set(nodes or [])

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if a == b:
            return None
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1

    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    return result if len(result) == len(all_nodes) else None
