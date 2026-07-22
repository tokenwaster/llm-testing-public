from collections import defaultdict
import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and track all nodes
    graph = defaultdict(set)
    edge_nodes = set()
    
    for a, b in edges:
        graph[a].add(b)
        edge_nodes.add(a)
        edge_nodes.add(b)
    
    # Add additional nodes if provided
    if nodes is not None:
        for node in nodes:
            edge_nodes.add(node)
    
    # Initialize in-degrees for all nodes
    in_degree = {node: 0 for node in edge_nodes}
    
    # Calculate in-degrees from edges
    for a, b in edges:
        if b in in_degree:
            in_degree[b] += 1
    
    # Use min-heap for Kahn's algorithm to get lexicographically smallest order
    heap = []
    for node in edge_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        # Process neighbors
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check if we processed all nodes (cycle detection)
    if len(result) != len(edge_nodes):
        return None
    
    return result
