import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree = defaultdict(int)
    
    all_nodes = set()
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if a == b:  # Self-loop is a cycle
            return None
        adj[a].add(b)
    
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)
    
    # Calculate in-degrees
    for neighbors in adj.values():
        for b in neighbors:
            in_degree[b] += 1
    
    # Initialize heap with nodes that have no incoming edges
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
    
    # Check for cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
