import heapq
from collections import defaultdict


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Return the lexicographically smallest topological ordering of the graph
    defined by `edges`, or None if the graph contains a cycle.

    - Each edge (a, b) means a must come before b.
    - Duplicate edges are ignored (they must not double-count indegrees).
    - A self-loop is treated as a cycle.
    - Extra isolated nodes from `nodes` are included in the output.
    """
    graph: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = defaultdict(int)
    all_nodes: set[str] = set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        if b not in graph[a]:
            graph[a].add(b)
            indegree[b] += 1

    if nodes:
        for n in nodes:
            all_nodes.add(n)

    # Start with all nodes that have no incoming edges (min-heap for
    # lexicographically smallest ordering).
    heap = [n for n in all_nodes if indegree[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If not every node was emitted, the graph contains a cycle.
    if len(result) != len(all_nodes):
        return None

    return result
