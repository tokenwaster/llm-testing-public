from typing import Optional
import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes
    node_set = set()
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        node_set.add(a)
        node_set.add(b)
    
    if nodes is not None:
        node_set.update(nodes)
    
    all_nodes = sorted(node_set)  # sort for consistent processing
    n = len(all_nodes)
    
    if n == 0:
        return []
    
    # Build adjacency list and in-degree count using a set to avoid duplicate edges
    adj = defaultdict(set)
    in_degree = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        if b not in adj[a]:  # only add edge once (handle duplicates)
            adj[a].add(b)
            in_degree[b] += 1
    
    # Initialize min-heap with all nodes having in-degree 0
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    
    while heap:
        # Always pick the lexicographically smallest available node
        current = heapq.heappop(heap)
        result.append(current)
        
        # Reduce in-degree for all neighbors
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If we couldn't process all nodes, there's a cycle
    if len(result) != n:
        return None
    
    return result
