import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by edges.
    Returns the lexicographically smallest topological ordering of all nodes.
    If a cycle is detected, returns None.
    """
    adj = {}
    in_degree = {}
    all_nodes = set()

    # Collect all nodes from the edges provided
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    # Add additional nodes if they are provided via the 'nodes' argument
    if nodes:
        for node in nodes:
            all_nodes.add(node)

    # Initialize adjacency list and in-degree count for all identified nodes
    for node in all_nodes:
        adj[node] = []
        in_degree[node] = 0

    # Build the graph structure and calculate the in-degree of each node
    for u, v in edges:
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

        # For every neighbor of the current node, decrement its in-degree
        for v in adj[u]:
            in_degree[v] -= 1
            # If a neighbor's in-degree reaches zero, it is now available to be processed
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # A valid topological sort must include all nodes present in the graph.
    # If the result length does not match the total number of unique nodes, a cycle exists.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
