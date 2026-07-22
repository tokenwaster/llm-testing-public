import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes from edges and optional nodes list
    node_set = set()
    if nodes:
        node_set.update(nodes)
    
    # Build unique edge set and detect self-loops
    unique_edges = set()
    for u, v in edges:
        node_set.add(u)
        node_set.add(v)
        if u == v:
            return None  # self-loop is a cycle
    
    # Build adjacency list and indegree counts using unique edges
    adj = defaultdict(list)
    indegree = {node: 0 for node in node_set}
    neighbor_sets = defaultdict(set)
    
    for u, v in unique_edges:
        neighbor_sets[u].add(v)
    
    for u in node_set:
        if u in neighbor_sets:
            for v in neighbor_sets[u]:
                adj[u].append(v)
                indegree[v] += 1
    
    # Initialize min-heap with zero indegree nodes
    heap = []
    for node in node_set:
        if indegree[node] == 0:
            heapq.heappush(heap, node)
    
    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(heap, v)
    
    # If not all nodes processed, there is a cycle
    if len(result) != len(node_set):
        return None
    
    return result
