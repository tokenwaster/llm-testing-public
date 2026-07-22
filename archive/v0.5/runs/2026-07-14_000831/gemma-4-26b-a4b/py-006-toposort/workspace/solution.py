import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges and nodes.
    Returns the lexicographically smallest ordering if no cycle exists, otherwise returns None.
    """
    all_nodes = set()
    # Add all nodes mentioned in the edges to our set of nodes
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Add additional nodes from the 'nodes' parameter if provided
    if nodes:
        all_nodes.update(nodes)

    # To handle duplicate edges correctly (so they don't artificially inflate in-degrees),
    # we use a set of unique edges.
    unique_edges = set(edges)

    # Initialize adjacency list and in-degree count for all nodes
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm uses a min-priority queue (min-heap) to ensure that
    # when multiple nodes are available (in-degree 0), we always pick the 
    # alphabetically first one, resulting in the lexicographically smallest order.
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

    # If the number of nodes in our result is equal to the total number of unique nodes,
    # then we have successfully found a valid topological ordering without cycles.
    if len(result) == len(all_nodes):
        return result
    else:
        # A cycle was detected (some nodes never reached an in-degree of 0).
        return None
