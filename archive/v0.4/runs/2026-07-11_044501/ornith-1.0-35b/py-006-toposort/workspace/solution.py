import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    
    # Collect all nodes from edges and check for self-loops
    for a, b in edges:
        if a == b:  # self-loop is a cycle
            return None
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add additional nodes if provided
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Build adjacency list (using sets to handle duplicate edges) and in-degree count
    adj = {node: set() for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        if a != b:  # self-loops already filtered above
            adj[a].add(b)
            in_degree[b] += 1
    
    # Initialize min-heap with nodes having zero in-degree
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If not all nodes were processed, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
