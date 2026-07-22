def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    import heapq
    
    # Collect all nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    
    # Build adjacency list and in-degree map
    adj = {}
    in_degree = {}
    edge_set = set()
    
    # Initialize nodes
    for node in all_nodes:
        adj[node] = []
        in_degree[node] = 0
    
    # Process edges (handle duplicates by using a set)
    for a, b in edges:
        if a not in adj:
            adj[a] = []
            in_degree[a] = 0
        if b not in adj:
            adj[b] = []
            in_degree[b] = 0
        
        # Only add edge if not duplicate
        if (a, b) not in edge_set:
            edge_set.add((a, b))
            adj[a].append(b)
            in_degree[b] += 1
    
    # Initialize heap with nodes having in-degree 0
    heap = []
    for node in adj:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    
    # Kahn's algorithm with min-heap for lexicographic ordering
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Check for cycles
    if len(result) != len(adj):
        return None
    
    return result
