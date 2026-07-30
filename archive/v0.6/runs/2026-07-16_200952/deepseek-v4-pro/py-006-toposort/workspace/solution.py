import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Gather all nodes that must appear
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        all_nodes.update(nodes)

    # Build graph using only unique edges to avoid double counting in-degrees
    unique_edges = set(edges)
    adj = {node: [] for node in all_nodes}
    indeg = {node: 0 for node in all_nodes}

    for a, b in unique_edges:
        if a == b:
            return None          # self-loop means cycle
        adj[a].append(b)
        indeg[b] += 1

    # Min-heap for lexicographically smallest available node
    heap = [node for node in all_nodes if indeg[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)

    if len(result) != len(all_nodes):
        return None              # cycle detected
    return result
