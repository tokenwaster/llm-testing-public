import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by edges.
    Returns the lexicographically smallest topological ordering using Kahn's algorithm with a min-heap.
    If a cycle is detected, returns None.
    """
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    
    # Add all nodes mentioned in edges to the set of all nodes
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    # Initialize adjacency list and in-degree count for each node
    adj = {node: set() for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for u, v in edges:
        # A self-loop is a cycle
        if u == v:
            return None
        
        # Only add unique dependencies to avoid incorrect in-degree counts
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1

    # Kahn's algorithm uses a min-heap to ensure the lexicographically smallest order
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
        # Otherwise, there was a cycle in the graph
        return None
