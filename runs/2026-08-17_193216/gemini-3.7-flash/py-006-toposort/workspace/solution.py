import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)

    adj: dict[str, list[str]] = {node: [] for node in all_nodes}
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}

    deduped_edges = set(edges)
    for u, v in deduped_edges:
        adj[u].append(v)
        in_degree[v] += 1

    heap = [node for node, deg in in_degree.items() if deg == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        curr = heapq.heappop(heap)
        result.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) == len(all_nodes):
        return result
    return None
