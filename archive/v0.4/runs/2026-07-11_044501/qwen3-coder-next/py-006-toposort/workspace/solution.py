import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and in-degree count
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Collect all nodes from edges
    all_nodes = set()
    
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        # Handle self-loop: if a == b, it's a cycle
        if a == b:
            return None
        graph[a].append(b)
        in_degree[b] += 1
    
    # Add additional nodes if provided
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)
    
    # Initialize in_degree for nodes with no incoming edges
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Use a min-heap to always pick the lexicographically smallest available node
    heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        # Pop the lexicographically smallest node with in-degree 0
        current = heapq.heappop(heap)
        result.append(current)
        
        # Decrease in-degree for all neighbors
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # If we haven't processed all nodes, there's a cycle
    if len(result) != len(all_nodes):
        return None
    
    return result
