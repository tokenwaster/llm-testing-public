import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and in-degree map
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if a == b:
            # self-loop is a cycle
            return None
        adj[a].append(b)
        in_degree[b] += 1

    if nodes:
        for n in nodes:
            all_nodes.add(n)

    # Ensure every node has an in-degree entry
    for n in all_nodes:
        if n not in in_degree:
            in_degree[n] = 0

    # Min-heap of available nodes (in-degree 0)
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
