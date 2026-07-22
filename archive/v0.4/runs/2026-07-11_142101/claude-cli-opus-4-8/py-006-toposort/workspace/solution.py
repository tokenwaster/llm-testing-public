import heapq
from collections import defaultdict


def topo_sort(edges, nodes=None):
    all_nodes = set()
    adj = defaultdict(set)
    indegree = defaultdict(int)

    if nodes:
        all_nodes.update(nodes)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in sorted(adj[n]):
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(all_nodes):
        return None
    return result
