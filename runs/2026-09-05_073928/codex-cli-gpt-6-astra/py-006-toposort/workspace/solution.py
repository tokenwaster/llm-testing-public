import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    adjacency: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    for node in nodes or []:
        adjacency.setdefault(node, set())
        indegree.setdefault(node, 0)

    for a, b in edges:
        adjacency.setdefault(a, set())
        adjacency.setdefault(b, set())
        indegree.setdefault(a, 0)
        indegree.setdefault(b, 0)
        if b not in adjacency[a]:
            adjacency[a].add(b)
            indegree[b] += 1

    available = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(available)
    result: list[str] = []

    while available:
        node = heapq.heappop(available)
        result.append(node)
        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    return result if len(result) == len(indegree) else None
