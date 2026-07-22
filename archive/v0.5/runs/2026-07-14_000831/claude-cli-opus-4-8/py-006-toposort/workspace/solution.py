import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}

    def ensure(n: str) -> None:
        if n not in adj:
            adj[n] = set()
            indeg[n] = 0

    if nodes:
        for n in nodes:
            ensure(n)

    for a, b in edges:
        ensure(a)
        ensure(b)

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

    heap = [n for n in adj if indeg[n] == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    if len(order) != len(adj):
        return None
    return order
