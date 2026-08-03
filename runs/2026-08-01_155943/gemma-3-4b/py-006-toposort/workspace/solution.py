def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by a list of edges.

    Args:
        edges: A list of tuples, where each tuple (a, b) represents an edge from node 'a' to node 'b'.
        nodes: An optional list of nodes that must be included in the sorted output, even if they have no incoming or outgoing edges.

    Returns:
        A list representing a topological ordering of all nodes in the graph. If a cycle is detected, returns None.
        The returned list is lexicographically smallest among possible valid orderings.
    """
    graph = {}
    in_degree = {}
    all_nodes = set()

    for u, v in edges:
        graph.setdefault(u, []).append(v)
        in_degree[v] = in_degree.get(v, 0) + 1
        all_nodes.add(u)
        all_nodes.add(v)

    if nodes is None:
        nodes = list(all_nodes)
    else:
        all_nodes.update(nodes)

    queue = [node for node in all_nodes if in_degree.get(node, 0) == 0]
    result = []

    while queue:
        node = min(queue)  # Lexicographically smallest
        queue.remove(node)
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(all_nodes):
        return None  # Cycle detected

    return result
