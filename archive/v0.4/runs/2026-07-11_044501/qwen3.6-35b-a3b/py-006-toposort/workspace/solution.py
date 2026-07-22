import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        all_nodes.update(nodes)
        
    in_degree = {node: 0 for node in all_nodes}
    adj = {node: [] for node in all_nodes}
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
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
                
    if len(result) < len(all_nodes):
        return None
    return result
