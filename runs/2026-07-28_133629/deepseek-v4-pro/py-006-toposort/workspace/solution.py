import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # collect all nodes
    all_nodes = set()
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    if nodes is not None:
        for n in nodes:
            all_nodes.add(n)
    
    adj = defaultdict(list)
    indegree = defaultdict(int)
    
    # initialize indegree for all nodes
    for n in all_nodes:
        indegree[n] = 0
        
    for a, b in edges:
        adj[a].append(b)
        indegree[b] += 1
        
    # min-heap with all nodes that have indegree 0
    heap = [n for n in all_nodes if indegree[n] == 0]
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
    else:
        return None
