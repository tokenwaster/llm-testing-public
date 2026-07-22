import heapq


def topo_sort(
    edges: list[tuple[str, str]],
    nodes: list[str] | None = None,
) -> list[str] | None:
    all_nodes = set(nodes or [])
    adjacency: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adjacency.setdefault(a, set())
        adjacency.setdefault(b, set())

    for node in all_nodes:
        adjacency.setdefault(node, set())
        indegree[node] = 0

    for a, b in edges:
        if b not in adjacency[a]:
            adjacency[a].add(b)
            indegree[b] += 1

    available = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(available)

    ordering: list[str] = []

    while available:
        node = heapq.heappop(available)
        ordering.append(node)

        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    return ordering if len(ordering) == len(all_nodes) else None
