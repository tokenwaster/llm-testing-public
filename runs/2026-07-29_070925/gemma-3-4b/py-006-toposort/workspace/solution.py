def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Topologically sorts a directed graph represented as a list of edges.

    Args:
        edges: A list of tuples (a, b), where a must come before b in the ordering.
        nodes: An optional list of nodes that must appear in the output, even if they have no incoming or outgoing edges.

    Returns:
        A topological ordering of all nodes, or None if the graph contains a cycle.
        If multiple valid orderings exist, returns the lexicographically smallest one.
    """

    graph = {}
    in_degree = {}
    all_nodes = set()

    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        if u not in graph:
            graph[u] = []
        graph[u].append(v)
        in_degree[v] = in_degree.get(v, 0) + 1
        if u not in in_degree:
            in_degree[u] = 0

    if nodes is None:
        nodes = sorted(list(all_nodes))  # Ensure all nodes are included even if they have no edges

    queue = [node for node in nodes if in_degree.get(node, 0) == 0]
    result = []

    while queue:
        u = min(queue)  # Lexicographically smallest
        queue.remove(u)
        result.append(u)

        if u in graph:
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

    if len(result) != len(all_nodes):
        return None  # Cycle detected

    return result
