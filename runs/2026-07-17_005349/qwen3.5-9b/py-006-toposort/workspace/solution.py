from collections import defaultdict
import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and collect all nodes from edges
    adj = defaultdict(set)
    edge_nodes = set()
    
    for a, b in edges:
        if a == b:  # Self-loop is a cycle
            return None
        adj[a].add(b)
        edge_nodes.add(a)
        edge_nodes.add(b)
    
    # Add additional nodes from the nodes parameter
    all_nodes = edge_nodes.copy()
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Initialize in-degrees for all nodes
    in_degree = {node: 0 for node in all_nodes}
    
    # Calculate in-degrees based on edges
    for a, b in edges:
        if a != b:  # Skip self-loops (already handled)
            adj[a].add(b)
            in_degree[b] += 1
    
    # Kahn's algorithm with min-heap for lexicographically smallest ordering
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        # Process neighbors
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check if all nodes were processed (no cycle)
    if len(result) != len(all_nodes):
        return None
    
    return result
