import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    all_nodes = set(nodes) if nodes is not None else set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    for u, v in edges:
        if u == v:
            return None

    adj: dict[str, list[str]] = {node: [] for node in all_nodes}
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}

    unique_edges = set(edges)
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1

    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        curr = heapq.heappop(heap)
        result.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) < len(all_nodes):
        return None

    return result
