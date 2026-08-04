import heapq


def topo_sort(edges, nodes=None):
    adj = {}
    indegree = {}

    def ensure(n):
        if n not in adj:
            adj[n] = set()
            indegree[n] = 0

    if nodes:
        for n in nodes:
            ensure(n)

    seen_edges = set()
    for a, b in edges:
        ensure(a)
        ensure(b)
        if a == b:
            return None
        if (a, b) in seen_edges:
            continue
        seen_edges.add((a, b))
        adj[a].add(b)
        indegree[b] += 1

    heap = [n for n in adj if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in adj[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(adj):
        return None
    return result
