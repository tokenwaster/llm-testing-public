import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set(nodes or [])
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj: dict[str, set[str]] = {n: set() for n in all_nodes}
    indegree: dict[str, int] = {n: 0 for n in all_nodes}
    for a, b in edges:
        if b not in adj[a]:  # ignore duplicate edges
            adj[a].add(b)
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for m in adj[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(order) != len(all_nodes):
        return None  # cycle (includes self-loops)
    return order
