import heapq
from collections import defaultdict


def topo_sort(
    edges: list[tuple[str, str]], nodes: list[str] | None = None
) -> list[str] | None:
    adj: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {}
    all_nodes_set: set[str] = set()

    for a, b in edges:
        adj[a].append(b)
        if b not in in_degree:
            in_degree[b] = 0
        in_degree[b] += 1
        all_nodes_set.add(a)
        all_nodes_set.add(b)

    # Initialize nodes that only appear as sources with in-degree 0
    for a, b in edges:
        if a not in in_degree:
            in_degree[a] = 0

    # Add extra nodes from the `nodes` parameter
    if nodes is not None:
        for n in nodes:
            all_nodes_set.add(n)
            if n not in in_degree:
                in_degree[n] = 0

    return _kahn(adj, in_degree, all_nodes_set)


def _kahn(
    adj: dict[str, list[str]],
    in_degree: dict[str, int],
    all_nodes: set[str],
) -> list[str] | None:
    heap: list[str] = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)

        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    return result if len(result) == len(all_nodes) else None
