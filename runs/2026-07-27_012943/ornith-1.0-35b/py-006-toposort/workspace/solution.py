import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, list[str]] = {}
    in_degree: dict[str, int] = {}

    def ensure_node(n: str) -> None:
        if n not in adj:
            adj[n] = []
            in_degree[n] = 0

    for a, b in edges:
        ensure_node(a)
        ensure_node(b)

    seen_edges: set[tuple[str, str]] = set()
    for a, b in edges:
        if (a, b) not in seen_edges:
            seen_edges.add((a, b))
            adj[a].append(b)
            in_degree[b] += 1

    if nodes is not None:
        for n in nodes:
            ensure_node(n)

    heap = [n for n in adj if in_degree[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    return result if len(result) == len(adj) else None
