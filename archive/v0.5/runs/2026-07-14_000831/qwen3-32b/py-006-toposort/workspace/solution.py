import heapq
from collections import defaultdict
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Check for self loops in edges
    for u, v in edges:
        if u == v:
            return None
    
    # Collect all unique nodes from edges and the 'nodes' parameter
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Build adjacency list and in-degree count
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    
    # Initialize min-heap with nodes of in-degree zero
    heap = []
    for node in all_nodes:
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
    
    # Check for cycles
    if len(result) != len(all_nodes):
        return None
    
    return result
