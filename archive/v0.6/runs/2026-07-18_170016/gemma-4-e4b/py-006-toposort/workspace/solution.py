import collections
import heapq
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> Optional[list[str]]:
    """
    Performs a topological sort on the given edges. 
    Returns the lexicographically smallest ordering if multiple exist.
    Returns None if a cycle is detected.
    """

    # 1. Identify all unique nodes
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    if nodes:
        all_nodes.update(nodes)

    total_nodes = len(all_nodes)

    # 2. Initialize graph structures
    adj = collections.defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}

    # 3. Build Graph and Calculate In-Degrees
    for u, v in edges:
        # Handle duplicate edges/self-loops gracefully by only adding unique dependencies
        if v not in adj[u]:
            adj[u].append(v)
            in_degree[v] += 1

    # 4. Initialize Min-Heap (Priority Queue)
    # The heap stores all nodes with an initial in-degree of 0.
    min_heap = []
    for node in sorted(list(all_nodes)): # Sorting ensures consistent initialization order if needed, though the heap handles priority
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)

    # 5. Kahn's Algorithm with Min-Heap
    result = []
    while min_heap:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(min_heap)
        result.append(u)

        # Process neighbors (dependencies)
        for v in adj[u]:
            in_degree[v] -= 1
            
            # If a neighbor's dependencies are met, add it to the heap
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # 6. Cycle Detection and Return
    if len(result) == total_nodes:
        return result
    else:
        # If we couldn't process all nodes, there must be a cycle
        return None
