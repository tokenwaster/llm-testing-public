import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Build graph and check for self-loops
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        adj[a].append(b)
        in_degree[b] += 1
    
    # Collect all nodes from edges
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add additional nodes if provided
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Initialize min-heap with nodes having in-degree 0
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        curr = heapq.heappop(heap)
        result.append(curr)
        
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If not all nodes are processed, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
