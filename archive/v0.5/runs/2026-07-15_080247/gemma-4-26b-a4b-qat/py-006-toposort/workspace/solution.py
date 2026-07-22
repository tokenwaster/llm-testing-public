import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph.
    Returns the lexicographically smallest topological ordering of all nodes.
    If a cycle is detected, returns None.
    """
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Initialize adjacency list and in-degree count
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Build the graph
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's algorithm using a min-heap for lexicographical order
    # Start with all nodes that have an in-degree of 0
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
                
    # If the result contains all nodes, a valid topological sort was found
    if len(result) == len(all_nodes):
        return result
    else:
        # A cycle exists if we couldn't include all nodes in the result
        return None
