from typing import Optional, Union
import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: Optional[list[str]] = None) -> Union[list[str], None]:
    """Return the lexicographically smallest topological ordering of all nodes in a directed graph, or None if a cycle exists.

    Args:
        edges: List of (a, b) pairs meaning "a must come before b".
        nodes: Optional list of additional isolated nodes that must appear in the result.

    Returns:
        A list representing a topological order, or None if no valid ordering exists.
    """
    # Build adjacency map and collect all known nodes (from edges + optional extra)
    adj: dict[str, set[str]] = {}
    all_nodes: set[str] = set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if a not in adj:
            adj[a] = set()
        adj[a].add(b)

    # Ensure any extra nodes are included (even if they have no edges)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
            if n not in adj:
                adj[n] = set()

    # Compute initial indegree counts based on unique incoming edges only.
    indegree: dict[str, int] = {n: 0 for n in all_nodes}
    for src, dests in adj.items():
        for dst in dests:
            if dst in indegree:
                indegree[dst] += 1

    # Initialize priority queue with all nodes having zero incoming edges.
    pq = [n for n, d in indegree.items() if d == 0]
    heapq.heapify(pq)

    result: list[str] = []

    while pq:
        u = heapq.heappop(pq)          # pick lexicographically smallest available node
        result.append(u)
        for v in adj.get(u, set()):
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(pq, v)

    # If not all nodes were processed, the graph contains a cycle.
    if len(result) < len(all_nodes):
        return None

    return result
