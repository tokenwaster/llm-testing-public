import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
            
    adj = defaultdict(list)
    in_degree = {n: 0 for n in all_nodes}
    
    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1
        
    heap = []
    for n in all_nodes:
        if in_degree[n] == 0:
            heapq.heappush(heap, n)
            
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
