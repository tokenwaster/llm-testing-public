import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # collect nodes and deduplicate edges
    nodes_set = set()
    edge_set = set()
    for a, b in edges:
        if a == b:          # self-loop is a cycle
            return None
        nodes_set.add(a)
        nodes_set.add(b)
        edge_set.add((a, b))

    if nodes:
        nodes_set.update(nodes)

    adj = defaultdict(set)
    indegree = {node: 0 for node in nodes_set}

    for a, b in edge_set:
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    heap = [node for node in nodes_set if indegree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj.get(u, []):
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(heap, v)

    if len(result) != len(nodes_set):
        return None
    return result
