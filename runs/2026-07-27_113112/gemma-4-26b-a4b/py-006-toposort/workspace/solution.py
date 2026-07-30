import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph using Kahn's algorithm.
    Returns the lexicographically smallest topological ordering if one exists, 
    otherwise returns None if a cycle is detected.
    """
    all_nodes = set()
    
    # Add nodes provided in the optional 'nodes' parameter
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)
            
    # Collect all nodes involved in edges and prepare for graph construction
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Initialize adjacency list and in-degree count for every node
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    # Build the graph structure
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Initialize a min-heap with all nodes that have an in-degree of 0.
    # Using a heap ensures we always pick the alphabetically first node available.
    queue = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(queue)
    
    result = []
    
    while queue:
        u = heapq.heappop(queue)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(queue, v)
                
    # If the result contains all nodes, it's a valid topological sort.
    # Otherwise, there was a cycle in the graph.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
