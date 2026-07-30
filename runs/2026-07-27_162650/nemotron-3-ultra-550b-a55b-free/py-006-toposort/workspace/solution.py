import heapq
from collections import defaultdict
from typing import List, Tuple, Optional

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> Optional[List[str]]:
    # Collect all nodes from edges and the optional nodes list
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes:
        all_nodes.update(nodes)

    # Build adjacency list and in-degree counts, ignoring duplicate edges
    graph = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}
    seen_edges = set()

    for a, b in edges:
        if a == b:
            return None  # self-loop is a cycle
        if (a, b) in seen_edges:
            continue
        seen_edges.add((a, b))
        graph[a].append(b)
        in_degree[b] += 1

    # Initialize min-heap with all nodes having in-degree 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If we couldn't process all nodes, there's a cycle
    if len(result) != len(all_nodes):
        return None
    return result
