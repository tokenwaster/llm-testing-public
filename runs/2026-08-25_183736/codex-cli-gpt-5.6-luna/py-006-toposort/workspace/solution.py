import heapq


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    all_nodes = set(nodes or [])
    adjacency: dict[str, list[str]] = {}
    indegree: dict[str, int] = {}

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, [])
        indegree[b] = indegree.get(b, 0) + 1
        indegree.setdefault(a, 0)

    for node in all_nodes:
        adjacency.setdefault(node, [])
        indegree.setdefault(node, 0)

    available = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(available)

    result = []
    while available:
        node = heapq.heappop(available)
        result.append(node)

        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    return result if len(result) == len(all_nodes) else None
