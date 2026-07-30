import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    if nodes is not None:
        all_nodes.update(nodes)
    
    indegree = {node: 0 for node in all_nodes}
    adj = {node: [] for node in all_nodes}
    
    for u, v in edges:
        if u == v:
            return None
        adj[u].append(v)
        indegree[v] += 1
    
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
