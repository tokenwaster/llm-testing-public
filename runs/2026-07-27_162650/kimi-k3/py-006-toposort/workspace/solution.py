import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adjacency: dict[str, set[str]] = {}
    in_degree: dict[str, int] = {}

    def ensure(node: str) -> None:
        if node not in adjacency:
            adjacency[node] = set()
            in_degree[node] = 0

    if nodes is not None:
        for node in nodes:
            ensure(node)

    for a, b in edges:
        ensure(a)
        ensure(b)
        if b not in adjacency[a]:  # ignore duplicate edges
            adjacency[a].add(b)
            in_degree[b] += 1

    # Kahn's algorithm with a min-heap for lexicographically smallest order.
    heap = [node for node, deg in in_degree.items() if deg == 0]
    heapq.heapify(heap)

    order: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for nxt in adjacency[node]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                heapq.heappush(heap, nxt)

    # If not all nodes were emitted, a cycle (or self-loop) exists.
    if len(order) != len(in_degree):
        return None
    return order
