import heapq
from typing import List, Optional, Tuple

def topo_sort(edges: List[Tuple[str, str]], nodes: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    Returns a topological ordering of the given directed graph.
    If a cycle exists, returns None.
    Uses Kahn's algorithm with a min-heap to produce the lexicographically smallest order.
    """
    # Collect all nodes from edges
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add optional extra nodes
    if nodes is not None:
        all_nodes.update(nodes)
    
    # Build adjacency list and indegree counts
    adj = {node: [] for node in all_nodes}
    indeg = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    
    # Min-heap for available nodes
    heap = []
    for node in all_nodes:
        if indeg[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    
    # If we didn't process all nodes, there is a cycle
    if len(result) != len(all_nodes):
        return None
    return result
