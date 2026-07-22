import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Handle default value for nodes
    if nodes is None:
        nodes = []
    
    # Collect all unique nodes from edges and the optional nodes list
    all_nodes = set(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Build graph
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    
    seen_edges = set()
    for u, v in edges:
        if u == v:
            return None
        
        edge_key = (u, v)
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            adj[u].append(v)
            in_degree[v] += 1
            
    # Initialize heap with nodes having 0 in-degree
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
                
    # Check for cycle
    if len(result) != len(all_nodes):
        return None
        
    return result
