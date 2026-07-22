import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes) if nodes else set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Deduplicate edges to correctly count in-degrees
    unique_edges = list(set(edges))
    
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Min-heap ensures lexicographically smallest ordering
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
