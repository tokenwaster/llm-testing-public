import heapq


def topo_sort(
    edges: list[tuple[str, str]],
    nodes: list[str] | None = None,
) -> list[str] | None:
    graph: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    for node in nodes or []:
        graph.setdefault(node, set())
        indegree.setdefault(node, 0)

    for a, b in edges:
        graph.setdefault(a, set())
        graph.setdefault(b, set())
        indegree.setdefault(a, 0)
        indegree.setdefault(b, 0)

        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    available = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(available)

    ordering: list[str] = []

    while available:
        node = heapq.heappop(available)
        ordering.append(node)

        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    return ordering if len(ordering) == len(indegree) else None
