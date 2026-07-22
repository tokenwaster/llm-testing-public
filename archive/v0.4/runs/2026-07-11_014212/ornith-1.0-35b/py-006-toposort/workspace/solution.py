import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree: dict[str, int] = {}
    
    all_nodes: set[str] = set()
    
    # Build graph from edges (using sets to deduplicate)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adj[a].add(b)
    
    # Add extra nodes if provided
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Compute in-degrees
    for node in all_nodes:
        in_degree[node] = 0
    for a in adj:
        for b in adj[a]:
            in_degree[b] += 1
    
    # Initialize min-heap with nodes having in-degree 0
    heap = []
    for n in all_nodes:
        if in_degree[n] == 0:
            heapq.heappush(heap, n)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
    
    # If not all nodes were processed, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
