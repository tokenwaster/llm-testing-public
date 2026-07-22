import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree = defaultdict(int)
    
    all_nodes = set()
    for u, v in edges:
        if u == v:
            return None  # self-loop is a cycle
        all_nodes.add(u)
        all_nodes.add(v)
        adj[u].add(v)
        
    if nodes:
        for n in nodes:
            all_nodes.add(n)
    
    # Calculate in-degrees from unique edges
    for u, neighbors in adj.items():
        for v in neighbors:
            in_degree[v] += 1
    
    # Initialize min-heap with nodes having zero in-degree
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
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
