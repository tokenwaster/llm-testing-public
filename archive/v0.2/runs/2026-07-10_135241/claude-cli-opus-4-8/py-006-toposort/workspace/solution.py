import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes: set[str] = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj: dict[str, set[str]] = defaultdict(set)
    indeg: dict[str, int] = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b not in adj[a]:  # dedupe so duplicate edges don't inflate indegree
            adj[a].add(b)
            indeg[b] += 1

    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in sorted(adj[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(all_nodes):
        return None
    return result
