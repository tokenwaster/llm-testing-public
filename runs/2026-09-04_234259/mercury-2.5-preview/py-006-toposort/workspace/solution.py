import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges and the optional nodes list
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes:
        all_nodes.update(nodes)
    
    if not all_nodes:
        return []

    # Build adjacency list and in-degree count
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Initialize in-degree for all nodes to 0
    for node in all_nodes:
        in_degree[node] = 0
        
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Initialize min-heap with nodes having in-degree 0
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
            
    result = []
    
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    # If result doesn't include all nodes, there is a cycle
    if len(result) != len(all_nodes):
        return None
        
    return result
