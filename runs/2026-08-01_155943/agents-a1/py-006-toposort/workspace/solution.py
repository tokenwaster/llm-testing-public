import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges and optional 'nodes' argument.
    node_set = set()
    
    if nodes is not None:
        for n in nodes:
            node_set.add(n)

    # Use a set to store edges, removing duplicates automatically.
    unique_edges = set(edges)

    for u, v in unique_edges:
        node_set.add(u)
        node_set.add(v)

    if not node_set:
        return []

    # Build adjacency list and compute in-degrees.
    adj = defaultdict(list)
    in_degree = {node: 0 for node in node_set}

    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1
    
    # Min-heap to store nodes with zero in-degree (available nodes).
    min_heap = []
    
    # Initialize heap with all available start nodes.
    for node in node_set:
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)

    result = []
    
    while min_heap:
        u = heapq.heappop(min_heap)
        result.append(u)
        
        # Iterate through neighbors of current node.
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # If we couldn't process all nodes, there is a cycle.
    if len(result) < len(node_set):
        return None
    
    return result
