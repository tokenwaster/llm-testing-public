import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges
    node_set = set()
    for u, v in edges:
        node_set.add(u)
        node_set.add(v)
    
    # Add isolated nodes if provided
    if nodes is not None:
        node_set.update(nodes)
        
    # If no nodes exist at all, return empty list
    if not node_set:
        return []

    # Initialize graph and in-degrees
    adj = defaultdict(list)
    in_degree = {node: 0 for node in node_set}
    
    # Build the graph
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    # Kahn's Algorithm with Min-Heap to ensure lexicographically smallest order
    min_heap = []
    for node in node_set:
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)
            
    result = []
    
    while min_heap:
        u = heapq.heappop(min_heap)
        result.append(u)
        
        # Process neighbors
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)
                
    # Check for cycle: if we didn't visit all nodes, there is a cycle
    if len(result) != len(node_set):
        return None
        
    return result
