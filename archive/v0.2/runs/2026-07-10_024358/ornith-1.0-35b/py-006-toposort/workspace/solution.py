import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes:
        for n in nodes:
            all_nodes.add(n)

    adj = {n: [] for n in all_nodes}
    in_degree = {n: 0 for n in all_nodes}

    for a, b in edges:
        adj[a].append(b)
        in_degree[b] += 1

    heap = []
    for n in all_nodes:
        if in_degree[n] == 0:
            heapq.heappush(heap, n)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    return result if len(result) == len(all_nodes) else None
