import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    adjacency: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    def add_node(node: str) -> None:
        if node not in adjacency:
            adjacency[node] = set()
            indegree[node] = 0

    for node in nodes or []:
        add_node(node)

    for a, b in edges:
        add_node(a)
        add_node(b)
        if b not in adjacency[a]:
            adjacency[a].add(b)
            indegree[b] += 1

    available = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(available)

    ordering: list[str] = []

    while available:
        node = heapq.heappop(available)
        ordering.append(node)

        for successor in adjacency[node]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                heapq.heappush(available, successor)

    if len(ordering) != len(adjacency):
        return None

    return ordering
