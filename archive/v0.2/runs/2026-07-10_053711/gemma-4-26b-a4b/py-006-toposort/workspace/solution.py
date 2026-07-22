import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges and optional additional nodes.
    Returns the lexicographically smallest valid ordering using Kahn's algorithm with a min-heap.
    If a cycle is detected, returns None.
    """
    all_nodes = set()
    # Add all nodes mentioned in the edges
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Add additional nodes if provided
    if nodes is not None:
        all_nodes.update(nodes)

    # Initialize adjacency list and in-degree count for all identified nodes
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    # Build the graph structure
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Initialize a min-heap with nodes that have an in-degree of 0
    # Using a min-heap ensures we always pick the lexicographically smallest available node.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If the number of nodes in the sorted order matches the total number of unique nodes,
    # it means no cycle was detected and all nodes were processed.
    if len(order) == len(all_nodes):
        return order
    else:
        # A mismatch indicates a cycle (or self-loop) exists in the graph.
        return None
