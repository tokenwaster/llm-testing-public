import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes from edges and optional nodes list
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)

    # Build adjacency list (using sets to ignore duplicate edges) and in-degree counts
    adj: dict[str, set[str]] = {n: set() for n in all_nodes}
    indeg: dict[str, int] = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1

    # Min-heap for lexicographically smallest available node
    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    if len(result) != len(all_nodes):
        return None
    return result
