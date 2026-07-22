import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Return the lexicographically smallest topological ordering of the given
    directed graph, or None if the graph contains a cycle.
    """
    graph: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}
    all_nodes: set[str] = set()

    def ensure_node(n: str) -> None:
        graph.setdefault(n, set())
        indeg.setdefault(n, 0)
        all_nodes.add(n)

    if nodes:
        for n in nodes:
            ensure_node(n)

    for a, b in edges:
        ensure_node(a)
        ensure_node(b)

        if a == b:
            # Self-loop is a cycle.
            return None

        # Avoid double-counting duplicate edges.
        if b not in graph[a]:
            graph[a].add(b)
            indeg[b] += 1

    heap = [n for n in all_nodes if indeg[n] == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)

    if len(order) != len(all_nodes):
        return None
    return order
