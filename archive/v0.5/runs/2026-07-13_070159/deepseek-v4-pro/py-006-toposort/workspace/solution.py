import heapq
from typing import List, Optional, Tuple

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> Optional[List[str]]:
    # Build graph and in-degree counts
    in_degree = {}
    graph = {}
    
    # Initialize with nodes from edges
    for a, b in edges:
        if a not in in_degree:
            in_degree[a] = 0
            graph[a] = []
        if b not in in_degree:
            in_degree[b] = 0
            graph[b] = []
        # Self-loop detection
        if a == b:
            return None
        graph[a].append(b)
        in_degree[b] += 1
    
    # Add extra nodes if provided
    if nodes:
        for node in nodes:
            if node not in in_degree:
                in_degree[node] = 0
                graph[node] = []
    
    # Min-heap for Kahn's algorithm
    heap = []
    for node, deg in in_degree.items():
        if deg == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        # Pick smallest available node
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If result doesn't contain all nodes, there is a cycle
    if len(result) != len(in_degree):
        return None
    
    return result
