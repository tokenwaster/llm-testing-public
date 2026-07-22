import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    for u, v in edges:
        if u == v:
            return None
        all_nodes.add(u)
        all_nodes.add(v)
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1
            
    if nodes:
        for n in nodes:
            all_nodes.add(n)
            
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
