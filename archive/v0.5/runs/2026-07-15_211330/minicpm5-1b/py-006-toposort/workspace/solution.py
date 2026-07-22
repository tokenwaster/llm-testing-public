import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Build adjacency list and indegree counts
    adj = defaultdict(list)
    indegree = defaultdict(int)
    
    for a, b in edges:
        adj[a].append(b)
        indegree[b] += 1
    
    # Determine all nodes to consider (from edges and optional nodes list)
    graph_nodes = set()
    if nodes is not None:
        graph_nodes.update(nodes)
    for a, b in edges:
        graph_nodes.add(a)
        graph_nodes.add(b)
    
    # Initialize available nodes (indegree 0) with min-heap
    available = []
    for node in graph_nodes:
        if indegree.get(node, 0) == 0:
            heapq.heappush(available, node)
    
    result = []
    while available:
        node = heapq.heappop(available)
        result.append(node)
        
        # Decrease indegree of neighbors
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, neighbor)
    
    # Check for cycle: if any node with indegree > 0 remains (should not happen if graph is DAG)
    if len(result) != len(graph_nodes):
        return None
    
    return result
