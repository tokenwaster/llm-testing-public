import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build the set of all nodes
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    # Build adjacency list and in-degree count
    adj: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}

    for a, b in edges:
        if a == b:
            # Self-loop is a cycle
            return None
        adj[a].append(b)
        in_degree[b] += 1

    # Initialize min-heap with all nodes that have in-degree 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        # Pick the lexicographically smallest available node
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If we didn't process all nodes, there's a cycle
    if len(result) != len(all_nodes):
        return None

    return result
