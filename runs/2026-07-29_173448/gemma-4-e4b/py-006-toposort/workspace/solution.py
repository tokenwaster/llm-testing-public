import collections
import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the graph defined by edges. 
    Returns the lexicographically smallest valid ordering, or None if a cycle exists.
    """

    # 1. Collect all unique nodes (N_set)
    n_set = set()
    for u, v in edges:
        n_set.add(u)
        n_set.add(v)
    if nodes is not None:
        n_set.update(nodes)

    # 2. Initialize graph structures
    adj = {node: set() for node in n_set}
    in_degree = {node: 0 for node in n_set}

    # 3. Build graph and calculate initial in-degrees
    for u, v in edges:
        # Handle duplicate edges/self-loops by using sets for adjacency
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1

    # 4. Initialize Min-Heap (Priority Queue) with starting nodes
    pq = []
    for node in sorted(list(n_set)): # Sorting here ensures deterministic initial population order
        if in_degree[node] == 0:
            heapq.heappush(pq, node)

    result = []
    
    # 5. Kahn's Algorithm execution (using Min-Heap for lexicographical requirement)
    while pq:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(pq)
        result.append(u)
        
        # Iterate through neighbors in sorted order to ensure consistent tie-breaking 
        # when updating degrees, though standard Kahn's algorithm only requires processing all unique neighbors.
        # Sorting neighbors here helps maintain determinism if multiple nodes hit zero degree simultaneously later.
        sorted_neighbors = sorted(list(adj[u]))

        for v in sorted_neighbors:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(pq, v)

    # 6. Check for cycles and return result
    if len(result) == len(n_set):
        return result
    else:
        # Cycle detected
        return None
