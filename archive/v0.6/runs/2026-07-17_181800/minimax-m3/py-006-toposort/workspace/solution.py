import heapq
from collections import defaultdict


def topo_sort(edges, nodes=None):
    adjacency = defaultdict(set)
    in_degree = {}
    all_nodes = set()

    # Collect every node that must appear in the output.
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    # Initialize in-degree counters for all known nodes.
    for n in all_nodes:
        in_degree[n] = 0

    # Build the graph; using a set for adjacency deduplicates edges.
    for a, b in edges:
        if b not in adjacency[a]:
            adjacency[a].add(b)
            in_degree[b] += 1

    # Kahn's algorithm with a min-heap yields the lexicographically smallest
    # valid topological ordering.
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None
    return result
