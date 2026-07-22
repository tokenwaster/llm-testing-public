import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes = set()
    
    if nodes:
        all_nodes.update(nodes)
    
    # Add nodes from edges
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Build graph and in-degree count
    graph = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    
    # Process edges, handling duplicates and self-loops
    seen_edges = set()
    for a, b in edges:
        # Check for self-loop
        if a == b:
            return None
        
        # Handle duplicates - only process each edge once
        edge = (a, b)
        if edge not in seen_edges:
            seen_edges.add(edge)
            graph[a].append(b)
            in_degree[b] += 1
    
    # Initialize heap with nodes that have in-degree 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    
    # Kahn's algorithm with min-heap for lexicographic ordering
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check if all nodes were processed (cycle detection)
    if len(result) != len(all_nodes):
        return None
    
    return result
