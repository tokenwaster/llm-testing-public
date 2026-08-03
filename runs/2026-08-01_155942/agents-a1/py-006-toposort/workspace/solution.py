import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """Perform topological sort with lexicographically smallest ordering."""
    
    # Build adjacency list and in-degree counts. Nodes mentioned in edges are included automatically.
    adj = defaultdict(list)  # a -> [b, c, ...] means a must come before b (edges a->b)
    in_degree = {}           # maps node to its current in-degree
    
    all_nodes = set()        # tracks every unique node we need to include
    
    for a, b in edges:
        if a == b:  # self-loop is a cycle; return None immediately
            return None
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Include additional nodes from the `nodes` parameter (if provided).
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)
    
    # Initialize each node's in-degree to 0.
    for node in all_nodes:
        in_degree[node] = 0
    
    # Build adjacency list and compute initial in-degrees from edges.
    for a, b in edges:
        adj[a].append(b)       # keep duplicates; we'll deduplicate later when decrementing
        in_degree[b] += 1
    
    # Use a min-heap to always pick the alphabetically smallest available node.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        
        # Process each outgoing edge from `current`.
        for neighbor in adj[current]:
            if neighbor not in all_nodes:
                continue  # should never happen, but skip just in case.
            
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If we didn't include every node, there is a cycle.
    if len(result) != len(all_nodes):
        return None
    
    return result
