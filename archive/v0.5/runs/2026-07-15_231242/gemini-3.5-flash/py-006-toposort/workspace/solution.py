import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Build adjacency list and calculate in-degrees
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in edges:
        if u == v:
            # Self-loop is a cycle
            return None
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's algorithm with a min-heap for lexicographical order
    # Initialize heap with all nodes having in-degree 0
    heap = [node for node, deg in in_degree.items() if deg == 0]
    heapq.heapify(heap)
    
    order = []
    while heap:
        curr = heapq.heappop(heap)
        order.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
                
    # If the order doesn't contain all nodes, there is a cycle
    if len(order) < len(all_nodes):
        return None
        
    return order
