import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build graph and calculate in-degrees
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    # Add edges and detect self-loops
    for a, b in edges:
        if a == b:
            # Self-loop is a cycle
            return None
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Add additional nodes
    if nodes:
        all_nodes.update(nodes)
    
    # Initialize in_degree for all nodes that don't have it
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    # Find all nodes with in-degree 0 and add to min-heap
    queue = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(queue, node)
    
    result = []
    while queue:
        # Pop the lexicographically smallest node
        node = heapq.heappop(queue)
        result.append(node)
        
        # Reduce in-degree for neighbors
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(queue, neighbor)
    
    # Check if all nodes were processed (detects cycles)
    if len(result) != len(all_nodes):
        return None
    
    return result
