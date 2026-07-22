import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph.
    Returns the lexicographically smallest ordering if multiple valid orderings exist.
    Returns None if a cycle is detected.
    """
    # Collect all unique nodes from edges and the optional nodes list
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)

    # Build adjacency list and calculate in-degrees for all unique nodes
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm using a min-heap to ensure the lexicographically smallest order.
    # Start with all nodes that have an in-degree of 0.
    queue = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(queue)

    result = []
    while queue:
        # Always pick the alphabetically first available node
        u = heapq.heappop(queue)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            # If in-degree becomes 0, it is now a candidate for the next position in the sort
            if in_degree[v] == 0:
                heapq.heappush(queue, v)

    # If the result list does not contain all nodes, there must be a cycle (including self-loops).
    if len(result) != len(all_nodes):
        return None

    return result
