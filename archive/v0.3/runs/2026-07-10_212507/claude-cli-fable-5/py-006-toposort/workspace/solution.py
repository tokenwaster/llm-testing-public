def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """Lexicographically smallest topological order (Kahn's algorithm with a
    min-heap), or None if the graph contains a cycle."""
    import heapq

    adj: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    def ensure(node: str) -> None:
        if node not in indegree:
            indegree[node] = 0
            adj[node] = set()

    for a, b in edges:
        ensure(a)
        ensure(b)
        if b not in adj[a]:  # ignore duplicate edges
            adj[a].add(b)
            indegree[b] += 1

    if nodes:
        for n in nodes:
            ensure(n)

    heap = [n for n, d in indegree.items() if d == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for m in adj[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(order) != len(indegree):
        return None  # cycle detected
    return order
