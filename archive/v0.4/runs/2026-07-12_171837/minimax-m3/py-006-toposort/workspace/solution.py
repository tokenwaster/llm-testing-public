import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes that must appear in the output
    all_nodes = set(nodes) if nodes else set()

    # Self-loops are cycles; detect them up front
    for a, b in edges:
        if a == b:
            return None
        all_nodes.add(a)
        all_nodes.add(b)

    # Build adjacency list and in-degree map
    adj = {node: set() for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}

    for a, b in edges:
        # Skip duplicate edges so in-degree isn't inflated
        if b not in adj[a]:
            adj[a].add(b)
            in_degree[b] += 1

    # Kahn's algorithm with a min-heap for lexicographically smallest order
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If we couldn't process every node, a cycle exists
    if len(result) != len(all_nodes):
        return None

    return result
