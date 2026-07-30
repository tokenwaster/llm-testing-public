import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    all_nodes: set[str] = set(nodes or [])
    adjacency: dict[str, set[str]] = {}

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adjacency.setdefault(a, set()).add(b)

    indegree: dict[str, int] = {node: 0 for node in all_nodes}
    for a, successors in adjacency.items():
        for b in successors:
            indegree[b] += 1

    available = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(available)

    ordering: list[str] = []

    while available:
        node = heapq.heappop(available)
        ordering.append(node)

        for successor in adjacency.get(node, ()):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                heapq.heappush(available, successor)

    return ordering if len(ordering) == len(all_nodes) else None
