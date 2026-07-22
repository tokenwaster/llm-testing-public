import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges and optional additional nodes.
    Returns the lexicographically smallest ordering if one exists, otherwise returns None.
    """
    # Collect all unique nodes involved in the graph
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    # Initialize adjacency list and in-degree counts
    adj = {node: set() for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for u, v in edges:
        # A self-loop is a cycle; Kahn's algorithm will naturally detect this,
        # but we must ensure it's handled by counting the edge.
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1

    # Use a min-heap to always pick the lexicographically smallest available node
    queue = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(queue)

    result = []
    while queue:
        u = heapq.heappop(queue)
        result.append(u)

        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(queue, v)

    # If the result contains all nodes, no cycle exists
    if len(result) == len(all_nodes):
        return result
    else:
        return None
