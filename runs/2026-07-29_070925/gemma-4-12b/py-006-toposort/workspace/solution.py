import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Returns the lexicographically smallest topological ordering of a directed graph.
    If a cycle exists, returns None.
    
    Args:
        edges: A list of (a, b) pairs where 'a' must precede 'b'.
        nodes: An optional list of additional nodes to include in the sort.
        
    Returns:
        A list of strings representing the topological order, or None if a cycle is found.
    """
    # Collect all unique nodes from both edges and the provided nodes list
    all_nodes = set()
    if nodes:
        for node in nodes:
            all_nodes.add(node)
    
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    # Initialize adjacency list and in-degree counts
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm with a min-heap ensures that we always pick the
    # lexicographically smallest available node among those with an in-degree of zero.
    min_heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(min_heap)

    result = []
    while min_heap:
        u = heapq.heappop(min_heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # If the result contains all nodes, a valid topological sort was found.
    # Otherwise, it means there is at least one cycle or self-loop in the graph.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
