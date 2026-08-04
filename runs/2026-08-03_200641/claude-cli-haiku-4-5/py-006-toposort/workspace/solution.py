def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    from heapq import heappush, heappop
    from collections import defaultdict
    
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    # Process edges
    added_edges = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        
        # Self-loop is a cycle
        if a == b:
            return None
        
        # Only add edge if we haven't seen it before (ignore duplicates)
        if (a, b) not in added_edges:
            added_edges.add((a, b))
            graph[a].append(b)
            in_degree[b] += 1
    
    # Add additional nodes
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)
    
    # Kahn's algorithm with min-heap for lexicographic order
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heappush(heap, node)
    
    result = []
    while heap:
        node = heappop(heap)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heappush(heap, neighbor)
    
    # Check if all nodes were processed
    if len(result) != len(all_nodes):
        return None
    
    return result
