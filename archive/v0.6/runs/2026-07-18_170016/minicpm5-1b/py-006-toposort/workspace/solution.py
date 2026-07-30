import heapq
from typing import List, Optional, Tuple

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> List[str] | None:
    # Collect all nodes from edges and optional additional nodes
    if nodes is None:
        all_nodes = set()
        for a, b in edges:
            all_nodes.add(a)
            all_nodes.add(b)
    else:
        all_nodes = set()
        for a, b in edges:
            all_nodes.add(a)
            all_nodes.add(b)
        for node in nodes:
            all_nodes.add(node)

    # Check for self-loops and cycles immediately
    for a, b in edges:
        if a == b:
            return None

    # Build adjacency list and indegree counts
    adj = {node: [] for node in all_nodes}
    indegree = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        adj[a].append(b)
        indegree[b] += 1

    # Kahn's algorithm with min-heap (lexicographically smallest first)
    heap = []
    processed = set()

    # Initialize heap with nodes having indegree 0
    for node in all_nodes:
        if indegree[node] == 0:
            heapq.heappush(heap, node)

    result = []
    while heap:
        node = heapq.heappop(heap)
        if node in processed:
            continue
        result.append(node)
        processed.add(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0 and neighbor not in result:
                heapq.heappush(heap, neighbor)

    # Check if all nodes were processed (no cycle)
    if len(result) != len(all_nodes):
        return None

    return result
