import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Build adjacency list and in-degree count
    in_degree = {node: 0 for node in all_nodes}
    graph = defaultdict(set)
    
    for a, b in edges:
        # Check for self-loop
        if a == b:
            return None
        # Avoid duplicate edges affecting in-degree
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1
    
    # Kahn's algorithm with min-heap for lexicographic ordering
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in sorted(graph[node]):  # sort for determinism, though heap handles order
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    if len(result) != len(all_nodes):
        return None
    
    return result
