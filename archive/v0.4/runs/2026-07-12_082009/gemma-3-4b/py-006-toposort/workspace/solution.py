def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by a list of edges.

    Args:
        edges: A list of tuples representing the edges in the graph. Each tuple (a, b)
               indicates that node 'a' must come before node 'b'.
        nodes: An optional list of nodes that should be included in the topological
               ordering even if they have no incoming or outgoing edges.

    Returns:
        A list representing a valid topological ordering of all nodes in the graph,
        or None if the graph contains a cycle.  The lexicographically smallest
        topological sort is returned when multiple orderings are possible.
    """
    graph = {}
    in_degree = {}

    # Build the graph and calculate in-degrees
    for u, v in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append(v)
        in_degree[v] = in_degree.get(v, 0) + 1
        if u not in in_degree:
            in_degree[u] = 0

    # Add nodes from the input if they are not already present
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    if nodes is not None:
        for node in nodes:
            if node not in all_nodes:
                all_nodes.add(node)
                in_degree[node] = 0  # Initialize in-degree for new nodes

    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    # Find nodes with an in-degree of 0
    queue = [node for node in in_degree if in_degree[node] == 0]
    result = []

    while queue:
        u = min(queue)  # Lexicographically smallest
        queue.remove(u)
        result.append(u)

        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # Check for cycles
    if len(result) != len(all_nodes):
        return None

    # Add missing nodes to the result if specified
    if nodes is not None:
        for node in nodes:
            if node not in result:
                result.append(node)

    return result
