import heapq
from collections import defaultdict

def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    """
    Performs a topological sort on a directed graph.
    Returns the lexicographically smallest ordering if no cycle exists, otherwise returns None.
    """
    all_nodes = set()
    # Add all nodes mentioned in edges to the set of all nodes
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Add additional nodes from the 'nodes' parameter if provided
    if nodes is not None:
        for node in nodes:
            all_nodes.add(node)

    # Build adjacency list and calculate in-degrees for all nodes
    adj = defaultdict(list)
    in_degree = {node: 0 for node in all_nodes}

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Kahn's algorithm using a min-heap to ensure lexicographical order
    # Initialize the heap with all nodes that have an in-degree of 0
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        
        # For every neighbor of the current node, decrement its in-degree
        for v in adj[u]:
            in_degree[v] -= 1
            # If in-degree becomes 0, add it to the heap for processing
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # If the number of nodes in the result matches the total number of unique nodes,
    # then no cycle was detected and a valid topological sort was found.
    if len(result) == len(all_nodes):
        return result
    else:
        # A cycle exists if not all nodes were included in the topological order
        return None
