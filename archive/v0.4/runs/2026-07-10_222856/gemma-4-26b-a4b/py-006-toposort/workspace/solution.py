import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges and optional additional nodes.
    Returns the lexicographically smallest topological ordering if no cycle exists,
    otherwise returns None.
    """
    # Identify all unique nodes in the graph
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)

    # Initialize adjacency list and in-degree count for each node
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    # Populate the adjacency list and calculate in-degrees
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm using a min-heap to ensure lexicographical smallest order.
    # The heap will store all nodes that currently have an in-degree of zero.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    topo_order = []
    while heap:
        u = heapq.heappop(heap)
        topo_order.append(u)

        for v in adj[u]:
            in_degree[v] -= 1
            # If in-degree becomes zero, the node is now available to be processed
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If the topological order contains all nodes, no cycle was detected.
    # Otherwise, a cycle exists (some nodes were never added to topo_order).
    if len(topo_order) == len(all_nodes):
        return topo_order
    else:
        return None
