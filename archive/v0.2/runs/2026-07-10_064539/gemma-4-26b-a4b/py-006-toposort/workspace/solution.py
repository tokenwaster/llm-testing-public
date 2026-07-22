import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges and additional nodes.
    Returns the lexicographically smallest topological ordering if no cycle exists.
    If a cycle is detected (including self-loops), returns None.
    """
    all_nodes = set()
    
    # Identify all nodes from edges and check for self-loops
    for u, v in edges:
        if u == v:
            return None  # A self-loop is a cycle
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Add additional nodes if provided
    if nodes:
        all_nodes.update(nodes)
    
    # Build adjacency list and in-degree count using unique edges
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Using a set of edges to handle duplicate edges correctly
    unique_edges = set(edges)
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's algorithm with a min-heap for lexicographical order
    # Initialize heap with all nodes that have an in-degree of 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    # If the result contains all nodes, we found a valid topological sort
    if len(result) == len(all_nodes):
        return result
    else:
        # Otherwise, there must be a cycle in the graph
        return None
