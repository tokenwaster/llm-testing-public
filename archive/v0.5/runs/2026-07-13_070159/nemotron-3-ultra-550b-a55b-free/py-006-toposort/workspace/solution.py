import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Collect all nodes from edges and the optional nodes list
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes:
        all_nodes.update(nodes)
    
    # Build adjacency list and indegree counts, checking for self-loops
    adj = defaultdict(list)
    indegree = {node: 0 for node in all_nodes}
    seen_edges = set()
    for a, b in edges:
        if a == b:
            return None  # self-loop indicates a cycle
        if (a, b) in seen_edges:
            continue  # ignore duplicate edges
        seen_edges.add((a, b))
        adj[a].append(b)
        indegree[b] += 1
    
    # Initialize min-heap with all nodes that have indegree 0
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
    
    # If we processed all nodes, return the ordering; otherwise there's a cycle
    return result if len(result) == len(all_nodes) else None
