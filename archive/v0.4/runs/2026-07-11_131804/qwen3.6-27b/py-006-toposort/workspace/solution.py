from __future__ import annotations
import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
            
    graph = defaultdict(set)
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in edges:
        if v not in graph[u]:
            graph[u].add(v)
            in_degree[v] += 1
            
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
            
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    if len(result) != len(all_nodes):
        return None
        
    return result
