import heapq
from typing import List, Tuple, Optional

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> Optional[List[str]]:
    # Collect all nodes from edges and optional node list
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    # Deduplicate edges to avoid double-counting dependencies
    unique_edges = set(edges)

    # Build adjacency list and in-degree map
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    for a, b in unique_edges:
        adj[a].append(b)
        in_degree[b] += 1

    # Kahn's algorithm using a min-heap for lexicographically smallest order
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    result = []

    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If not all nodes are processed, there is a cycle
    if len(result) != len(all_nodes):
        return None
    return result
