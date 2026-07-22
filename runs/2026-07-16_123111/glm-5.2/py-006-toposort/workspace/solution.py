import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build graph
    adj: dict[str, set[str]] = defaultdict(set)
    indeg: dict[str, int] = defaultdict(int)
    all_nodes: set[str] = set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        # self-loop is a cycle
        if a == b:
            return None
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)

    # Ensure every node has an indegree entry
    for n in all_nodes:
        if n not in indeg:
            indeg[n] = 0

    # Min-heap of available nodes (indegree 0)
    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in sorted(adj.get(n, ())):
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(all_nodes):
        return None
    return result
