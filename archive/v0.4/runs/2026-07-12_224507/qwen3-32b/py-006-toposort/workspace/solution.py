import heapq
from collections import defaultdict
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Check for self-loops in edges
    for a, b in edges:
        if a == b:
            return None
    
    unique_edges = set()
    for a, b in edges:
        unique_edges.add((a, b))
    
    all_nodes = set()
    for a, b in unique_edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    heap = []
    result = []
    
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    if len(result) != len(all_nodes):
        return None
    else:
        return result
