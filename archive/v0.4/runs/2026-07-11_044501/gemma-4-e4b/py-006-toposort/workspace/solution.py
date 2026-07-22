import heapq
from collections import defaultdict, deque

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on the given dependencies (edges).
    Returns the lexicographically smallest valid ordering. Returns None if a cycle exists.
    """

    # 1. Identify all unique nodes
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes:
        all_nodes.update(nodes)

    # 2. Initialize graph structures (Adjacency List and In-Degree map)
    adj = defaultdict(set)
    in_degree = {node: 0 for node in all_nodes}

    # Use a set of unique edges to prevent overcounting degrees due to duplicate input edges
    unique_edges = set()
    for u, v in edges:
        if (u, v) not in unique_edges:
            adj[u].add(v)
            in_degree[v] += 1
            unique_edges.add((u, v))

    # Convert sets to sorted lists for deterministic neighbor processing later
    sorted_adj = {node: sorted(list(neighbors)) for node, neighbors in adj.items()}


    # 3. Initialize Min-Heap (Priority Queue) with starting nodes (in_degree == 0)
    min_heap = []
    for node in all_nodes:
        if in_degree[node] == 0:
            heapq.heappush(min_heap, node)

    # 4. Kahn's Algorithm Execution
    result = []
    processed_count = 0

    while min_heap:
        # Pop the lexicographically smallest available node
        u = heapq.heappop(min_heap)
        result.append(u)
        processed_count += 1

        # Process neighbors (v) of u in sorted order
        for v in sorted_adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(min_heap, v)

    # 5. Cycle Detection and Final Check
    if processed_count != len(all_nodes):
        return None  # Cycle detected
    else:
        return result
