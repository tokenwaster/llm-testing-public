import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges. 
    Returns the lexicographically smallest valid ordering, or None if a cycle exists.
    """
    
    # 1. Initialize graph structures and collect all unique nodes
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    if nodes:
        all_nodes.update(nodes)

    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
        
        # Handle self-loops immediately as they guarantee a cycle
        if u == v:
            return None 
        
        adj[u].append(v)
        in_degree[v] += 1

    # Ensure all nodes, even isolated ones or sources/sinks not in edges, are initialized
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    # 2. Initialize the min-heap (Priority Queue) with starting nodes (in_degree == 0)
    min_heap = []
    for node in sorted(list(all_nodes)): # Sorting ensures consistent initial processing order if multiple start nodes exist
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)

    # 3. Kahn's Algorithm using Min-Heap
    result = []
    
    while min_heap:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(min_heap)
        result.append(u)
        
        # Process neighbors (v must come after u)
        # We sort neighbors to ensure deterministic processing if multiple paths exist, 
        # although the heap handles the primary tie-breaking rule.
        for v in sorted(adj[u]):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # 4. Cycle Detection and Final Check
    if len(result) == len(all_nodes):
        return result
    else:
        # If we couldn't process all nodes, there must be a cycle remaining
        return None
