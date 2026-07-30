import heapq
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Check for self loops in any edge (including duplicates)
    for a, b in edges:
        if a == b:
            return None

    unique_edges = set(edges)

    # Collect all nodes from edges and 'nodes' parameter
    nodes_in_edges = set()
    for a, b in edges:
        nodes_in_edges.add(a)
        nodes_in_edges.add(b)
    
    additional_nodes: set[str] = set() if nodes is None else set(nodes)
    total_nodes_set = nodes_in_edges.union(additional_nodes)

    # If there are no nodes (edges and nodes list both empty), return empty list
    if not total_nodes_set:
        return []

    # Build adjacency list and in-degree count
    adj = {node: [] for node in total_nodes_set}
    in_degree = {node: 0 for node in total_nodes_set}

    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1

    # Initialize min-heap with nodes of in-degree 0
    heap = []
    for node in total_nodes_set:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result = []

    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # Check for cycles (if not all nodes processed)
    if len(result) != len(total_nodes_set):
        return None

    return result
