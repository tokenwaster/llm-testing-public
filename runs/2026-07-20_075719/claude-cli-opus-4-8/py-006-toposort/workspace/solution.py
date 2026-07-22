import heapq
from collections import defaultdict


def topo_sort(edges, nodes=None):
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)

    adj = defaultdict(set)
    indegree = defaultdict(int)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    seen_edges = set()
    for a, b in edges:
        if a == b:
            return None  # self-loop is a cycle
        if (a, b) in seen_edges:
            continue  # skip duplicate edges
        seen_edges.add((a, b))
        adj[a].add(b)
        indegree[b] += 1

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nb in sorted(adj[node]):
            indegree[nb] -= 1
            if indegree[nb] == 0:
                heapq.heappush(heap, nb)

    if len(result) != len(all_nodes):
        return None  # cycle detected

    return result
