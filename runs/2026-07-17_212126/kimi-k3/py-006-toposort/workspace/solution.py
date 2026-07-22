import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes: set[str] = set(nodes) if nodes else set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adjacency: dict[str, set[str]] = {n: set() for n in all_nodes}
    in_degree: dict[str, int] = {n: 0 for n in all_nodes}

    # Use sets to ignore duplicate edges; a self-loop leaves in_degree >= 1,
    # which is correctly detected as a cycle below.
    for a, b in edges:
        if b not in adjacency[a]:
            adjacency[a].add(b)
            in_degree[b] += 1

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nxt in adjacency[node]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(result) != len(all_nodes):
        return None
    return result
