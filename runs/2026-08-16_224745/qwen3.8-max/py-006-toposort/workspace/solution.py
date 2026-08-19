import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes: set[str] = set(nodes) if nodes is not None else set()

    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    adj: dict[str, set[str]] = {node: set() for node in all_nodes}
    indegree: dict[str, int] = {node: 0 for node in all_nodes}

    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indegree[b] += 1

    heap = [node for node in all_nodes if indegree[node] == 0]
    heapq.heapify(heap)

    order: list[str] = []

    while heap:
        node = heapq.heappop(heap)
        order.append(node)

        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(order) != len(all_nodes):
        return None

    return order
