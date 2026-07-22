import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by edges and optional extra nodes.
    Returns the lexicographically smallest ordering or None if a cycle is detected.
    """
    # 1. Identify all unique nodes in the graph
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes:
        for node in nodes:
            all_nodes.add(node)
    
    # 2. Build the adjacency list and calculate in-degrees for all nodes
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # 3. Initialize a min-heap with nodes that have an in-degree of 0
    # Using a heap ensures we always pick the lexicographically smallest node available.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    # 4. Kahn's algorithm to find the topological sort
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    # 5. If the result contains all nodes, a valid topological sort was found.
    # Otherwise, there is at least one cycle in the graph.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
