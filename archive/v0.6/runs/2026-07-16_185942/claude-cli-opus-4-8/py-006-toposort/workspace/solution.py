import heapq
from collections import defaultdict


def topo_sort(edges, nodes=None):
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)

    adj = defaultdict(set)
    indegree = defaultdict(int)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    for node in all_nodes:
        indegree.setdefault(node, 0)

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nxt in sorted(adj[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(result) != len(all_nodes):
        return None

    return result
