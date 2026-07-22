import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj: dict[str, list[str]] = {}
    indegree: dict[str, int] = {}

    def ensure(node: str) -> None:
        if node not in adj:
            adj[node] = []
            indegree[node] = 0

    if nodes is not None:
        for node in nodes:
            ensure(node)

    for a, b in edges:
        ensure(a)
        ensure(b)
        adj[a].append(b)
        indegree[b] += 1

    heap = [node for node in adj if indegree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(adj):
        return None
    return result
