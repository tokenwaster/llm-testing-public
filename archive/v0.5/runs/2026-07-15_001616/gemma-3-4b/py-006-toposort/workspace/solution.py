def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by a list of edges.

    Args:
        edges: A list of tuples representing the edges in the graph. Each tuple (a, b)
               indicates that node 'a' must come before node 'b'.
        nodes: An optional list of nodes that should be included in the topological sort
               even if they have no incoming or outgoing edges.

    Returns:
        A list representing a valid topological ordering of all nodes in the graph,
        or None if the graph contains a cycle. The returned ordering is lexicographically smallest.
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
        nodes = list(all_nodes)
    else:
        all_nodes.update(nodes)

    queue = [node for node in all_nodes if in_degree.get(node, 0) == 0]
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
    else:
        return result
