import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph represented by edges and an optional 
    list of additional nodes. Returns the lexicographically smallest ordering or None if 
    a cycle is detected.
    """
    # Identify all unique nodes from both the edges and the provided nodes list.
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        all_nodes.update(nodes)

    # Initialize adjacency list and in-degree counts for all identified nodes.
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    # Build the graph structure. Duplicate edges are handled by incrementing in-degrees multiple times.
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm using a min-heap to ensure lexicographically smallest order at each step.
    # Only nodes with an initial in-degree of 0 are added to the heap.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        # Pop the alphabetically smallest available node with an in-degree of 0.
        u = heapq.heappop(heap)
        result.append(u)
        
        # For each neighbor, decrement its in-degree and add to heap if it becomes 0.
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If the result list contains all nodes, a valid topological sort was found.
    # Otherwise, there is at least one cycle in the graph (including self-loops).
    if len(result) == len(all_nodes):
        return result
    else:
        return None
