import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by edges and an optional 
    list of additional nodes. Returns the lexicographically smallest ordering or None if 
    a cycle is detected.

    Args:
        edges: A list of (u, v) tuples where u must come before v.
        nodes: An optional list of nodes to include in the output even if they have no edges.

    Returns:
        A lexicographically smallest topological ordering as a list of strings, 
        or None if a cycle exists.
    """
    # Identify all unique nodes from both edges and the provided nodes list
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        all_nodes.update(nodes)

    # Initialize adjacency list and in-degree counts for all identified nodes
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    # Build the graph structure
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm using a min-heap to ensure lexicographical order at each step
    # A node is available for selection if its in-degree is zero.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        
        # For every neighbor of the current node, decrement its in-degree
        for v in adj[u]:
            in_degree[v] -= 1
            # If a neighbor's in-degree reaches zero, it becomes available for selection
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If the result list contains all nodes, no cycle was found; otherwise, return None
    if len(result) != len(all_nodes):
        return None
    
    return result
