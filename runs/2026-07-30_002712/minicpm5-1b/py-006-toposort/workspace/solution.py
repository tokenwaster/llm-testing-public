import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes: from edges and optional nodes (if provided)
    if nodes is not None:
        nodes_set = set(nodes)
    else:
        for a, b in edges:
            nodes_set.add(a)
            nodes_set.add(b)

    # Check for self-loop immediately; if found, return None as it's a cycle.
    for a, b in edges:
        if a == b:
            return None

    all_nodes = list(nodes_set)  # convert to list for indexing

    # Build adjacency list and indegree counts
    adj = defaultdict(set)
    indegree = {node: 0 for node in all_nodes}

    for a, b in edges:
        adj[a].add(b)          # edge a -> b (a must come before b)
        indegree[b] += 1

    # Initialize min-heap with nodes having indegree 0
    heap = []
    for node in all_nodes:
        if indegree[node] == 0:
            heapq.heappush(heap, node)

    order = []
    processed_any = set()
    while heap:
        u = heapq.heappop(heap)
        # Skip if already processed to avoid duplicates (though we push only when indegree becomes 0)
        if u in processed_any:
            continue
        processed_any.add(u)
        order.append(u)

        # Process outgoing edges of u
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] < 0:   # cycle detected (negative indegree means a node depends on itself indirectly)
                return None
            if indegree[v] == 0:
                heapq.heappush(heap, v)

    # After processing all candidates, check for any remaining nodes that should be included?
    # Actually Kahn's algorithm ensures all nodes are processed if graph is a DAG.
    # If some node still has positive indegree (i.e., not processed), it indicates a cycle,
    # but we already checked for negative indegree during decrement. However, 
    # to be safe: verify that all nodes were eventually added to order.
    if len(order) != len(all_nodes):
        return None  # This means some nodes were never removed from the heap

    return order
