import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    
    # Deduplicate edges to avoid incorrect in-degree counts
    unique_edges = set(edges)
    for u, v in unique_edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Initialize adjacency list and in-degree map
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's algorithm using a min-heap for lexicographical order
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)
                
    # If the result contains all nodes, we found a valid topological sort
    if len(result) == len(all_nodes):
        return result
    return None
