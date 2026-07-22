import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes) if nodes else set()
    adj = defaultdict(set)
    
    for u, v in edges:
        adj[u].add(v)
        all_nodes.add(u)
        all_nodes.add(v)
        
    in_degree = {node: 0 for node in all_nodes}
    for u in adj:
        for v in adj[u]:
            in_degree[v] += 1
            
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    res = []
    while heap:
        u = heapq.heappop(heap)
        res.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    return res if len(res) == len(all_nodes) else None
