import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        graph[a].append(b)
        in_degree[b] += 1
        if a not in in_degree:
            in_degree[a] = 0
    
    heap = []
    for node in all_nodes:
        if in_degree.get(node, 0) == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    if len(result) == len(all_nodes):
        return result
    else:
        return None
