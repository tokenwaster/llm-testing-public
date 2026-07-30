from heapq import heappop, heappush


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    adjacency: dict[str, set[str]] = {}
    indegree: dict[str, int] = {}

    def add_node(node: str) -> None:
        if node not in indegree:
            indegree[node] = 0
            adjacency[node] = set()

    if nodes is not None:
        for node in nodes:
            add_node(node)

    for source, target in edges:
        add_node(source)
        add_node(target)
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1

    heap = [node for node, degree in indegree.items() if degree == 0]
    heap.sort()

    result: list[str] = []

    while heap:
        node = heappop(heap)
        result.append(node)

        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heappush(heap, neighbor)

    return result if len(result) == len(indegree) else None
