from collections import defaultdict
import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph = defaultdict(set)
    indegree = defaultdict(int)
    all_nodes = set()

    if nodes is not None:
        all_nodes.update(nodes)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    for n in all_nodes:
        if n not in indegree:
            indegree[n] = 0

    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nei in graph[node]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                heapq.heappush(heap, nei)

    if len(result) == len(all_nodes):
        return result
    return None
