import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges and the optional nodes list
    node_set = set()
    if nodes is not None:
        node_set.update(nodes)
    
    for u, v in edges:
        node_set.add(u)
        node_set.add(v)
        
    # Check for self-loops immediately as they indicate a cycle
    for u, v in edges:
        if u == v:
            return None
            
    # Build the graph and calculate in-degrees
    adj = defaultdict(list)
    in_degree = {node: 0 for node in node_set}
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Initialize min-heap with nodes that have no incoming edges
    min_heap = []
    for node in node_set:
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)
            
    result = []
    
    while min_heap:
        u = heapq.heappop(min_heap)
        result.append(u)
        
        # Iterate over neighbors
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)
                
    # If the number of visited nodes is less than total nodes, there is a cycle
    if len(result) != len(node_set):
        return None
        
    return result
