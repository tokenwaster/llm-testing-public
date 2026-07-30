import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from both the edges and the optional nodes list
    all_nodes = set()
    if nodes is not None:
        all_nodes.update(nodes)
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
    # Deduplicate edges to prevent issues with duplicate constraints
    unique_edges = set(edges)
    
    # Initialize in-degree and adjacency list
    in_degree = {node: 0 for node in all_nodes}
    adj = {node: [] for node in all_nodes}
    
    for u, v in unique_edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's algorithm with a min-heap to guarantee lexicographical order
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
                
    # If the result doesn't contain all nodes, there is a cycle
    if len(result) == len(all_nodes):
        return result
    else:
        return None
