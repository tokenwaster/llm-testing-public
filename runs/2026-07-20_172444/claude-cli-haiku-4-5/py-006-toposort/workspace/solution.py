import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph = defaultdict(set)
    all_nodes = set()
    
    for a, b in edges:
        if a == b:
            return None
        graph[a].add(b)
        all_nodes.add(a)
        all_nodes.add(b)
    
    if nodes:
        all_nodes.update(nodes)
    
    in_degree = {node: 0 for node in all_nodes}
    for a in graph:
        for b in graph[a]:
            in_degree[b] += 1
    
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    return result if len(result) == len(all_nodes) else None
