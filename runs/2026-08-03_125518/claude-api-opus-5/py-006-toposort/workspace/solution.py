import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """Return the lexicographically smallest topological ordering, or None if cyclic."""
    all_nodes: set[str] = set()
    if nodes:
        all_nodes.update(nodes)

    seen_edges: set[tuple[str, str]] = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        seen_edges.add((a, b))

    adj: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = {n: 0 for n in all_nodes}

    for a, b in seen_edges:
        adj[a].append(b)
        indeg[b] += 1

    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        cur = heapq.heappop(heap)
        result.append(cur)
        for nxt in adj[cur]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(heap, nxt)

    if len(result) != len(all_nodes):
        return None
    return result
