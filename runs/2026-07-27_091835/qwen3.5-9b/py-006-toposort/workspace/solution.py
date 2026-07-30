import heapq
from collections import defaultdict
from typing import List, Optional, Tuple


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges
    node_set = set()
    for a, b in edges:
        node_set.add(a)
        node_set.add(b)
    
    # If nodes parameter is provided, add those too
    if nodes:
        for n in nodes:
            node_set.add(n)
    
    all_nodes = set(node_set)
    
    # Build adjacency list and in-degree count
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    
    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    # Initialize all nodes with in_degree 0 (if not already set by edges)
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Use min-heap for lexicographically smallest ordering
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        
        # Process neighbors
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check if all nodes are included (no cycle)
    if len(result) != len(all_nodes):
        return None
    
    return result
