import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(list)
    in_degree: dict[str, int] = {}
    edge_nodes: set[str] = set()

    for a, b in edges:
        if a == b:  # self-loop → cycle
            return None
        adj[a].append(b)
        edge_nodes.add(a)
        edge_nodes.add(b)
        in_degree[b] = in_degree.get(b, 0) + 1

    for node in (nodes or []):
        if node not in in_degree:
            in_degree[node] = 0

    heap = [n for n, d in in_degree.items() if d == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    all_nodes = edge_nodes | set(nodes or [])
    return result if len(result) == len(all_nodes) else None
