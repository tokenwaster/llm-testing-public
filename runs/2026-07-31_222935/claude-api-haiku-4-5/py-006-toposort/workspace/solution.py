import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes = set()
    
    # Add nodes from edges
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add nodes from the nodes parameter
    if nodes is not None:
        all_nodes.update(nodes)
    
    # Build adjacency list and in-degree map
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Initialize in-degree for all nodes to 0
    for node in all_nodes:
        in_degree[node] = 0
    
    # Process edges
    seen_edges = set()
    for a, b in edges:
        # Check for self-loop
        if a == b:
            return None
        
        # Avoid counting duplicate edges multiple times
        edge = (a, b)
        if edge not in seen_edges:
            graph[a].append(b)
            in_degree[b] += 1
            seen_edges.add(edge)
    
    # Kahn's algorithm with min-heap for lexicographic ordering
    # Start with all nodes that have in-degree 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    
    while heap:
        # Pick the lexicographically smallest node
        node = heapq.heappop(heap)
        result.append(node)
        
        # Process neighbors
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check if all nodes were processed (no cycle)
    if len(result) != len(all_nodes):
        return None
    
    return result
