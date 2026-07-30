import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph.
    Returns the lexicographically smallest ordering if no cycle exists, otherwise returns None.
    """
    if nodes is None:
        nodes = []
    
    # Identify all unique nodes in the graph
    all_nodes = set(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Initialize adjacency list and in-degree count
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Use a set to handle duplicate edges so they don't inflate in-degrees.
    # A self-loop (a, a) will correctly result in an in-degree of at least 1.
    unique_edges = set()
    for u, v in edges:
        if (u, v) not in unique_edges:
            unique_edges.add((u, v))
            adj[u].append(v)
            in_degree[v] += 1
            
    # Kahn's algorithm using a min-heap to ensure the lexicographically smallest order.
    # The heap contains all nodes with an in-degree of 0.
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
                
    # If the number of nodes in the result is equal to the total number of unique nodes,
    # then a valid topological sort was found. Otherwise, there's a cycle.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
