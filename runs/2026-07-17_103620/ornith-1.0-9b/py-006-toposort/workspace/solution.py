import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    in_degree = {}

    # Detect self-loops and build adjacency with unique edges
    for a, b in edges:
        if a == b:
            return None
        adj[a].add(b)

    edge_nodes = set()
    for a, b in edges:
        edge_nodes.add(a)
        edge_nodes.add(b)

    # Initialize in-degrees to 0 for all nodes mentioned in edges
    for node in edge_nodes:
        in_degree[node] = 0

    # Count in-degrees from unique edges (excluding self-loops already filtered)
    for a in adj:
        for b in adj[a]:
            in_degree[b] += 1

    # Add extra nodes if provided, ensuring they appear even with no edges
    all_nodes = set(edge_nodes)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)

    # Ensure every node has an entry in in_degree
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    # Seed the min-heap with zero-in-degree nodes (lexicographic order via heap)
    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If not all nodes were processed, a cycle exists
    return result if len(result) == len(all_nodes) else None
