import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes from edges and optional nodes list
    nodes_in_edges = set()
    for a, b in edges:
        nodes_in_edges.add(a)
        nodes_in_edges.add(b)
    if nodes is not None:
        nodes_in_edges.update(nodes)
    all_nodes = list(nodes_in_edges)
    
    # Initialize in-degree and adjacency list
    in_degree = {node: 0 for node in all_nodes}
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    # Initialize heap with nodes having in-degree 0
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
    
    # Check if all nodes were processed (no cycles)
    if len(result) == len(all_nodes):
        return result
    else:
        return None
