import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Deduplicate edges to avoid incorrect in-degree counts
    unique_edges = set()
    for a, b in edges:
        unique_edges.add((a, b))
    
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    
    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1
    
    # Collect all nodes from edges
    all_nodes = set()
    for a, b in unique_edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add optional nodes that must appear even if they have no edges
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Initialize in_degree for all nodes (some might have 0)
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Kahn's algorithm with min-heap for lexicographically smallest ordering
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
    
    # If not all nodes are processed, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
