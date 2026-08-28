import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, list[str]] = {}
    indegree: dict[str, int] = {}

    def ensure(n: str) -> None:
        if n not in adj:
            adj[n] = []
        if n not in indegree:
            indegree[n] = 0

    for a, b in edges:
        ensure(a)
        ensure(b)
        adj[a].append(b)
        indegree[b] += 1

    if nodes:
        for n in nodes:
            ensure(n)

    # A self-loop is a cycle; Kahn's algorithm will detect it via the length
    # check below, but we can short-circuit explicitly.
    for a, b in edges:
        if a == b:
            return None

    heap = [n for n in indegree if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(indegree):
        return None

    return result
