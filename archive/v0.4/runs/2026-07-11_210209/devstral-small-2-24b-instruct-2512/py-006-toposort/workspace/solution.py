import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and in-degree count
    adj = {}
    in_degree = {}

    # Initialize with all nodes from edges
    for a, b in edges:
        if a not in adj:
            adj[a] = []
        if b not in adj:
            adj[b] = []
        adj[a].append(b)
        in_degree[b] = in_degree.get(b, 0) + 1
        in_degree[a] = in_degree.get(a, 0)  # Ensure a is in in_degree even if it has no incoming edges

    # Add nodes from the nodes parameter if provided
    if nodes:
        for node in nodes:
            if node not in adj:
                adj[node] = []
            in_degree[node] = in_degree.get(node, 0)

    # Initialize min-heap with nodes that have zero in-degree
    heap = []
    for node in in_degree:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result = []

    while heap:
        current = heapq.heappop(heap)
        result.append(current)

        for neighbor in adj.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # Check if all nodes were processed (no cycle)
    if len(result) != len(in_degree):
        return None

    return result
