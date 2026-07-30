import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes: set[str] = set()
    if nodes:
        all_nodes.update(nodes)

    # Track unique edges; self-loops are cycles
    unique_edges: set[tuple[str, str]] = set()
    for a, b in edges:
        if a == b:
            return None
        unique_edges.add((a, b))
        all_nodes.add(a)
        all_nodes.add(b)

    # Build adjacency list and in-degree map
    adj: dict[str, list[str]] = {node: [] for node in all_nodes}
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}

    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1

    # Kahn's algorithm with a min-heap for lexicographically smallest order
    heap: list[str] = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
