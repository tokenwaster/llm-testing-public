import heapq

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    if nodes is None:
        nodes = []
    all_nodes = set(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    
    adj = {node: [] for node in all_nodes}
    in_degree = {node: 0 for node in all_nodes}
    
    for a, b in edges:
        if a == b:
            return None
        adj[a].append(b)
        in_degree[b] += 1
    
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for nb in adj[node]:
            in_degree[nb] -= 1
            if in_degree[nb] == 0:
                heapq.heappush(heap, nb)
    
    if len(result) != len(all_nodes):
        return None
    return result
