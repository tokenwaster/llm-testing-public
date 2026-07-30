import heapq
from collections import defaultdict
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Check for self-loops in edges
    unique_edges = set()
    all_nodes_set = set()

    for u, v in edges:
        if u == v:
            return None
        unique_edges.add((u, v))
        all_nodes_set.add(u)
        all_nodes_set.add(v)

    # Add additional nodes if provided
    if nodes is not None:
        for node in nodes:
            all_nodes_set.add(node)

    # Build adjacency list and in-degree dictionary
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes_set}

    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Initialize priority queue with nodes of in-degree zero
    heap = []
    for node in all_nodes_set:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # Check for cycles
    if len(result) != len(all_nodes_set):
        return None

    return result
