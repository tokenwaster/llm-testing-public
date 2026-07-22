import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, set[str]] = defaultdict(set)
    indeg: dict[str, int] = defaultdict(int)

    def ensure(n: str) -> None:
        if n not in adj:
            adj[n] = set()
            indeg[n] = 0

    for a, b in edges:
        ensure(a)
        ensure(b)
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

    if nodes is not None:
        for n in nodes:
            ensure(n)

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

    if len(result) != len(indeg):
        return None
    return result
