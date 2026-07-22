import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
        
    unique_edges = set(edges)
    for a, b in unique_edges:
        all_nodes.add(a)
        all_nodes.add(b)
        
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    
    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1
        
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
