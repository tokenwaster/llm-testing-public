from collections import defaultdict
import heapq
from typing import list, tuple, Optional

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given edges. 
    Returns the lexicographically smallest ordering, or None if a cycle exists.
    """
    
    # 1. Initialization and Graph Building
    adj = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()

    if nodes:
        for node in nodes:
            all_nodes.add(node)
    
    # Process edges to build graph structure and calculate degrees
    for u, v in edges:
        # Handle self-loops (which are cycles) and duplicate edges 
        # by using sets for adjacency list.
        if v not in adj[u]:
            adj[u].add(v)
            in_degree[v] += 1
        
        all_nodes.add(u)
        all_nodes.add(v)

    # Ensure all nodes (even isolated ones or sources/sinks) are tracked in in_degree
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    # 2. Initialize Min-Heap (Priority Queue)
    # Start with all nodes having an in-degree of 0.
    min_heap = []
    for node in sorted(list(all_nodes)): # Sorting ensures deterministic initial heap population
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)

    # 3. Kahn's Algorithm with Min-Heap
    result = []
    while min_heap:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(min_heap)
        result.append(u)
        
        # Process neighbors (v) of u
        # Sorting neighbors ensures deterministic processing order if multiple 
        # nodes become available simultaneously, although the heap handles the final choice.
        for v in sorted(list(adj[u])):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # 4. Cycle Detection and Return
    if len(result) == len(all_nodes):
        return result
    else:
        # If the number of nodes in the result is less than the total number of unique nodes, a cycle exists.
        return None
