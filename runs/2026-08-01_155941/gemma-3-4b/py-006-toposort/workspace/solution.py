def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by a list of edges.

    Args:
        edges: A list of tuples representing the edges in the graph. Each tuple (a, b)
               means that node 'a' must come before node 'b'.
        nodes: An optional list of nodes that must be included in the topological
               ordering even if they have no incoming or outgoing edges.

    Returns:
        A list representing a valid topological ordering of all nodes, or None if the graph contains a cycle.
        If provided, ensures that all nodes listed in `nodes` are present in the output.
    """

    if nodes is None:
        nodes = []  # Default to empty list if no nodes are explicitly provided.

    graph = {}
    in_degree = {}
    all_nodes = set(nodes)

    for u, v in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append(v)
        in_degree[v] = in_degree.get(v, 0) + 1
        all_nodes.add(u)
        all_nodes.add(v)

    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

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

    if len(result) != len(all_nodes):
        return None  # Cycle detected

    if nodes:
      for node in nodes:
          if node not in result:
              return None

    return result
