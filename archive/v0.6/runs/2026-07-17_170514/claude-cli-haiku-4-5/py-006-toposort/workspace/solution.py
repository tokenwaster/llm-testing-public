from heapq import heappush, heappop, heapify
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    # Process edges
    for a, b in edges:
        if b not in graph[a]:  # Only count each edge once
            in_degree[b] += 1
        graph[a].add(b)
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add additional nodes
    if nodes:
        all_nodes.update(nodes)
    
    # Kahn's algorithm with min-heap for lexicographic ordering
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapify(heap)
    
    result = []
    while heap:
        node = heappop(heap)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heappush(heap, neighbor)
    
    return result if len(result) == len(all_nodes) else None
