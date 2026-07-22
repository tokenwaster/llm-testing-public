import heapq
from collections import defaultdict, deque

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given graph edges.
    Returns the lexicographically smallest ordering, or None if a cycle exists.
    """
    
    # 1. Initialize structures and identify all nodes
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    # Add nodes from edges
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
        # Build graph and count dependencies (in-degrees)
        adj[u].append(v)
        in_degree[v] += 1

    # Add optional standalone nodes
    if nodes:
        for node in nodes:
            all_nodes.add(node)
            # Ensure these nodes are initialized in degree map if they have no edges
            if node not in in_degree:
                in_degree[node] = 0

    # Ensure all nodes, even those with only outgoing edges or isolated, are tracked
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
        # Also ensure they exist as keys in adj if they have no outgoing edges listed yet
        if node not in adj:
             adj[node] = []

    # 2. Initialize Min-Heap (Priority Queue)
    pq = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(pq, node)

    # 3. Kahn's Algorithm with Priority Queue
    result = []
    
    while pq:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(pq)
        result.append(u)
        
        # Process neighbors (v must come after u)
        for v in adj[u]:
            in_degree[v] -= 1
            
            # If v's dependencies are met, add it to the available set
            if in_degree[v] == 0:
                heapq.heappush(pq, v)

    # 4. Cycle Detection and Return
    if len(result) != len(all_nodes):
        # If we couldn't process all nodes, there must be a cycle
        return None
    else:
        return result
