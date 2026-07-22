import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    if nodes is None:
        all_nodes = set()
        for a, b in edges:
            all_nodes.add(a)
            all_nodes.add(b)
    else:
        all_nodes = set(nodes)
        for a, b in edges:
            all_nodes.add(a)
            all_nodes.add(b)

    # Build adjacency list and indegree counts
    adj = {}
    indegree = {}
    for u, v in edges:
        if u not in adj:
            adj[u] = []
        adj[u].append(v)
        indegree[v] = indegree.get(v, 0) + 1

    # Initialize min-heap with nodes having indegree 0
    heap = []
    for node in all_nodes:
        if indegree[node] == 0:
            heapq.heappush(heap, node)

    ordering = []

    while heap:
        x = heapq.heappop(heap)
        ordering.append(x)
        # For each neighbor of x (nodes reachable from x via outgoing edges), decrease indegree by 1
        for v in adj.get(x, []):
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(heap, v)

    # If ordering contains all nodes (or only processed those with indegree 0), return it.
    if len(ordering) == len(all_nodes):
        return ordering
    else:
        return None
