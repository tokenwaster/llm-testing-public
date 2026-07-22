import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the graph defined by edges.
    Returns the lexicographically smallest valid ordering, or None if a cycle exists.
    """

    # 1. Identify all unique nodes and initialize structures
    all_nodes = set()
    unique_edges = set()
    for u, v in edges:
        unique_edges.add((u, v))
        all_nodes.add(u)
        all_nodes.add(v)

    if nodes:
        all_nodes.update(nodes)

    # Initialize adjacency list and in-degrees for all nodes
    adj = defaultdict(set)
    in_degree = {node: 0 for node in all_nodes}

    # 2. Build the graph structure (using unique dependencies only)
    for u, v in unique_edges:
        # Check if this dependency is new for adjacency list purposes
        if v not in adj[u]:
            adj[u].add(v)
            # Increment in-degree based on the unique dependency
            in_degree[v] += 1

    # 3. Initialize Min-Heap (Priority Queue) with starting nodes
    pq = []
    for node in sorted(list(all_nodes)): # Sort to ensure consistent initial heap population order
        if in_degree[node] == 0:
            heapq.heappush(pq, node)

    # 4. Kahn's Algorithm using Min-Heap
    result = []
    while pq:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(pq)
        result.append(u)

        # Process neighbors (must process in sorted order for deterministic behavior, 
        # although standard Kahn's doesn't require it, sorting ensures consistency 
        # if multiple paths lead to the same node later).
        neighbors = sorted(list(adj[u]))
        
        for v in neighbors:
            # Decrement dependency count
            in_degree[v] -= 1
            
            # If no more dependencies, add it to the pool of available nodes
            if in_degree[v] == 0:
                heapq.heappush(pq, v)

    # 5. Cycle Detection and Return
    if len(result) != len(all_nodes):
        return None  # Cycle detected
    else:
        return result
