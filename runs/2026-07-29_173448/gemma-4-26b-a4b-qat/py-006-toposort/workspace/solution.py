import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Returns the lexicographically smallest topological ordering of all nodes.
    If a cycle is detected, returns None.
    """
    # Collect all unique nodes from both edges and the optional nodes list
    all_nodes = set()
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    # Build the adjacency list and in-degree dictionary
    # Using a set for unique_edges to handle duplicate edges correctly
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    unique_edges = set(edges)

    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's Algorithm with a min-heap to ensure lexicographical smallest ordering
    # The heap contains all nodes currently having an in-degree of 0
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

    # If the number of nodes in the result is less than the total unique nodes, 
    # a cycle exists in the graph.
    if len(result) == len(all_nodes):
        return result
    else:
        return None
