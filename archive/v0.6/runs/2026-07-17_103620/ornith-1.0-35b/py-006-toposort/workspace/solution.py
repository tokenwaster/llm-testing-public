import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = {}
    in_degree = {}
    
    # Collect all nodes from edges
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add any additional nodes specified
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    # Initialize adjacency list and in-degree count for all nodes
    for node in all_nodes:
        adj[node] = []
        in_degree[node] = 0
    
    # Process edges to build the graph
    for a, b in edges:
        if a == b:
            return None  # Self-loop is a cycle
        adj[a].append(b)
        in_degree[b] += 1
    
    # Initialize min-heap with all nodes having in-degree 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        
        # Process neighbors and update their in-degrees
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If not all nodes were processed, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
