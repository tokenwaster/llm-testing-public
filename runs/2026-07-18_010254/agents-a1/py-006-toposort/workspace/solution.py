import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all unique nodes from edges and optional nodes list
    node_set = set(nodes) if nodes else set()
    for a, b in edges:
        node_set.add(a)
        node_set.add(b)

    # Build graph with deduplicated edges
    adj = defaultdict(set)
    indegree = defaultdict(int)
    for a, b in set(edges):  # remove duplicate edges
        adj[a].add(b)
        indegree[b] += 1

    # Ensure every node has an entry in indegree (default 0 if no incoming edges)
    for node in node_set:
        if node not in indegree:
            indegree[node] = 0

    # Initialize min-heap with nodes that have indegree 0
    heap = [node for node in node_set if indegree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    # If not all nodes were processed, there is a cycle
    if len(result) != len(node_set):
        return None

    return result
