import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree = defaultdict(int)
    
    # Process edges and detect self-loops
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        adj[a].add(b)
        in_degree[b] += 1
    
    # Collect all nodes from edges
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add additional nodes if provided
    if nodes:
        for node in nodes:
            all_nodes.add(node)
    
    # Initialize in-degrees for nodes with no incoming edges
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Build min-heap with nodes having in-degree 0
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
    
    # Check if we processed all nodes (cycle detection)
    if len(result) != len(all_nodes):
        return None
    
    return result
