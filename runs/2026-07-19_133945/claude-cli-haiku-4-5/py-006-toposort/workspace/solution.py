import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    
    # Build graph and track in-degrees
    graph = {}
    in_degree = {}
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Initialize graph and in_degree for all nodes
    for node in all_nodes:
        graph[node] = set()
        in_degree[node] = 0
    
    # Add edges (deduplicating)
    for a, b in edges:
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1
    
    # Find all nodes with in-degree 0
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
    
    # Check if all nodes are included (no cycle)
    if len(result) == len(all_nodes):
        return result
    else:
        return None
