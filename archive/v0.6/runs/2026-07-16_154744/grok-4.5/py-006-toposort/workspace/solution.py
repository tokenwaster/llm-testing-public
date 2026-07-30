from collections import defaultdict
import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    adj = defaultdict(set)
    all_nodes = set(nodes) if nodes else set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
        adj[a].add(b)

    indegree = {node: 0 for node in all_nodes}
    for a in adj:
        for b in adj[a]:
            indegree[b] += 1

    heap = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) == len(all_nodes):
        return result
    return None
