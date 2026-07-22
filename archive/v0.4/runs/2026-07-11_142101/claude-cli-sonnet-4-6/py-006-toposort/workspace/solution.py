import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set(nodes) if nodes else set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    for a, b in edges:
        if a == b:
            return None
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1

    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
