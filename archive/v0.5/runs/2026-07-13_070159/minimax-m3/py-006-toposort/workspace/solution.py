import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # A self-loop is a cycle, so return None immediately.
    for a, b in edges:
        if a == b:
            return None

    # Collect every node that must appear in the result.
    all_nodes: set[str] = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        all_nodes.update(nodes)

    # Build the graph while ignoring duplicate edges.
    adj: defaultdict[str, set[str]] = defaultdict(set)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    seen_edges: set[tuple[str, str]] = set()
    for a, b in edges:
        if (a, b) not in seen_edges:
            seen_edges.add((a, b))
            adj[a].add(b)
            in_degree[b] += 1

    # Kahn's algorithm: start with all in-degree-zero nodes in a min-heap
    # so the alphabetically smallest one is chosen at every step.
    heap: list[str] = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If we couldn't order every node, there must be a cycle.
    if len(result) != len(all_nodes):
        return None

    return result
