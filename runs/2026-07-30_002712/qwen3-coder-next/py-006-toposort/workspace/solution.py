import heapq
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: Optional[list[str]] = None) -> Optional[list[str]]:
    # Build adjacency list and in-degree count
    graph = {}  # node -> list of successors
    in_degree = {}
    
    # Collect all nodes from edges
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        
        if a not in graph:
            graph[a] = []
        graph[a].append(b)
        
        in_degree[b] = in_degree.get(b, 0) + 1
        if a not in in_degree:
            in_degree[a] = 0
    
    # Add additional nodes if provided
    if nodes is not None:
        for node in nodes:
            if node not in in_degree:
                in_degree[node] = 0
                graph[node] = []
    
    # Initialize min-heap with all nodes having in-degree 0
    heap = []
    for node, degree in in_degree.items():
        if degree == 0:
            heapq.heappush(heap, node)
    
    result = []
    
    while heap:
        # Pick the lexicographically smallest node
        current = heapq.heappop(heap)
        result.append(current)
        
        # Process all neighbors
        for neighbor in graph.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If we haven't processed all nodes, there's a cycle
    if len(result) != len(in_degree):
        return None
    
    return result
