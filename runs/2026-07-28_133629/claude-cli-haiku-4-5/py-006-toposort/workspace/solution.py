import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and in-degree map
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    # Process edges
    for a, b in edges:
        if a == b:
            # Self-loop is a cycle
            return None
        if b not in graph[a]:  # Avoid counting duplicate edges multiple times
            graph[a].add(b)
            in_degree[b] += 1
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add nodes from the nodes parameter
    if nodes:
        for node in nodes:
            all_nodes.add(node)
    
    # Ensure all nodes have in_degree
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Initialize heap with nodes that have in_degree 0
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
    
    # If we didn't process all nodes, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
