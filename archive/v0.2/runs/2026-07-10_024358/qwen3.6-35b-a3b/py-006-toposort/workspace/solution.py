import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes) if nodes is not None else set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    in_degree = {n: 0 for n in all_nodes}
    adj = {n: [] for n in all_nodes}
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    if len(result) != len(all_nodes):
        return None
    return result
