import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        all_nodes.update(nodes)
    
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    if len(result) != len(all_nodes):
        return None
    return result
