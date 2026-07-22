import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes or [])
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    adj = {node: set() for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Deduplicate edges to correctly count in-degrees
    for u, v in set(edges):
        if u == v:
            return None
        adj[u].add(v)
        in_degree[v] += 1
        
    # Initialize min-heap with all nodes having zero in-degree
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    return result if len(result) == len(all_nodes) else None
