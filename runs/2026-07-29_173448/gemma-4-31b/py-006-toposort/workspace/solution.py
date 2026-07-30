import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Returns a lexicographically smallest topological ordering of all nodes.
    If a cycle is detected, returns None.
    """
    # 1. Identify all unique nodes involved in the graph
    all_nodes_set = set()
    for u, v in edges:
        all_nodes_set.add(u)
        all_nodes_set.add(v)
    if nodes is not None:
        for n in nodes:
            all_nodes_set.add(n)

    # 2. To avoid incorrect in-degree counts, treat duplicate edges as a single constraint
    unique_edges = set(edges)

    # 3. Build adjacency list and calculate in-degrees
    adj = {node: [] for node in all_nodes_set}
    in_degree = {node: 0 for node in all_nodes_set}
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1

    # 4. Initialize a min-heap with nodes that have no incoming edges (in-degree 0).
    # A min-heap ensures we always pick the lexicographically smallest node available.
    queue = [node for node in all_nodes_set if in_degree[node] == 0]
    heapq.heapify(queue)

    result = []
    while queue:
        u = heapq.heappop(queue)
        result.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(queue, v)

    # 5. If the result list contains all nodes, we found a valid topological sort.
    # Otherwise, there is at least one cycle in the graph.
    if len(result) != len(all_nodes_set):
        return None

    return result
