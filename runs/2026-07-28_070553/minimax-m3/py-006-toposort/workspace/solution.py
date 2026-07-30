import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()

    # Process edges
    for a, b in edges:
        # A self-loop is a cycle
        if a == b:
            return None
        all_nodes.add(a)
        all_nodes.add(b)
        # Use a set to deduplicate edges
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1

    # Add any additional standalone nodes
    if nodes:
        all_nodes.update(nodes)

    # Ensure every node has an entry in in_degree
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    # Seed the min-heap with all nodes that have in-degree zero
    available = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(available)

    result = []
    while available:
        node = heapq.heappop(available)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(available, neighbor)

    # If we couldn't visit every node, a cycle exists
    if len(result) != len(all_nodes):
        return None

    return result
