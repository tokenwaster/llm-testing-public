def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    import heapq

    all_nodes = set(nodes or [])
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj = {n: set() for n in all_nodes}
    for a, b in edges:
        adj[a].add(b)

    indegree = {n: 0 for n in all_nodes}
    for a in adj:
        for b in adj[a]:
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in adj[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(all_nodes):
        return None
    return result
