import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}

    def add_node(n: str) -> None:
        if n not in adj:
            adj[n] = set()
            indeg[n] = 0

    if nodes is not None:
        for n in nodes:
            add_node(n)

    for a, b in edges:
        add_node(a)
        add_node(b)
        if b not in adj[a]:  # ignore duplicate edges
            adj[a].add(b)
            indeg[b] += 1

    # Kahn's algorithm with a min-heap for lexicographically smallest result
    heap = [n for n, d in indeg.items() if d == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    # If not all nodes were emitted, a cycle (or self-loop) exists
    if len(result) != len(indeg):
        return None
    return result
