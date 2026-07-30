import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes) if nodes else set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        
    adj = defaultdict(set)
    in_degree = {node: 0 for node in all_nodes}
    
    seen_edges = set()
    for a, b in edges:
        if (a, b) not in seen_edges:
            seen_edges.add((a, b))
            adj[a].add(b)
            in_degree[b] += 1
            
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
