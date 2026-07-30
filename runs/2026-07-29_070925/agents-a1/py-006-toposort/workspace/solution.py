import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges and optional parameter
    node_set = set()
    
    for u, v in edges:
        node_set.add(u)
        node_set.add(v)
        
    if nodes is not None:
        node_set.update(nodes)

    total_nodes = len(node_set)
    
    # Build graph with unique directed edges (u -> v) to handle duplicates naturally.
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
            
    # Calculate initial in-degrees based on the deduplicated edge set.
    in_degree = {node: 0 for node in node_set}
    for u in adj:
        for v in adj[u]:
            in_degree[v] += 1
            
    # Min-heap to store nodes with zero incoming edges, ensuring lexico smallest order.
    heap = [node for node, degree in in_degree.items() if degree == 0]
    heapq.heapify(heap)

    topo_order = []

    while heap:
        u = heapq.heappop(heap)
        topo_order.append(u)
        
        # Decrease in-degree of neighbors and add to heap if it becomes zero.
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If not all nodes are included, a cycle exists.
    if len(topo_order) < total_nodes:
        return None
        
    return topo_order
