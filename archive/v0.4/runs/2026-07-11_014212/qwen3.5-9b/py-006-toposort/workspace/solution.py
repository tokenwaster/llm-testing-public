import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes from edges and additional nodes
    all_nodes = set()
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    if nodes is not None:
        all_nodes.update(nodes)
    
    # Build adjacency list and in-degree count
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    
    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    # Initialize in_degree for all nodes (some might have 0)
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
