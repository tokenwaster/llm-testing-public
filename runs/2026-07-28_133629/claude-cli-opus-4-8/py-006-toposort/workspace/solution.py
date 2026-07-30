import heapq
from collections import defaultdict


def topo_sort(edges, nodes=None):
    graph = defaultdict(set)
    indegree = defaultdict(int)
    all_nodes = set()

    if nodes:
        all_nodes.update(nodes)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    for a, b in edges:
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nxt in sorted(graph[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(result) != len(all_nodes):
        return None

    return result
