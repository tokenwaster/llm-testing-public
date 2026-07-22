def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    import heapq
    
    # Collect all nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    
    # Collect nodes from edges
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Build adjacency list and in-degree map
    graph = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Process edges, handling duplicates
    seen_edges = set()
    for a, b in edges:
        # Self-loop is a cycle
        if a == b:
            return None
        
        # Add edge only if not already added (handle duplicates)
        if (a, b) not in seen_edges:
            graph[a].append(b)
            in_degree[b] += 1
            seen_edges.add((a, b))
    
    # Kahn's algorithm with min-heap for lexicographic order
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
    
    # Check if all nodes were processed (no cycle)
    if len(result) != len(all_nodes):
        return None
    
    return result
