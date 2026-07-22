import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    # Build graph and indegree
    adj = defaultdict(list)
    indegree = {node: 0 for node in all_nodes}
    seen_edges = set()
    
    for a, b in edges:
        if a == b:
            # self-loop is a cycle
            return None
        if (a, b) in seen_edges:
            continue
        seen_edges.add((a, b))
        adj[a].append(b)
        indegree[b] += 1
    
    # Initialize min-heap with nodes having indegree 0
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
    
    if len(result) != len(all_nodes):
        return None
    return result
