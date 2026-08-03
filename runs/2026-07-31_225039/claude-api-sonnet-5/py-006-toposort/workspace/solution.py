import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    all_nodes = set()
    if nodes:
        all_nodes.update(nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    graph = {n: set() for n in all_nodes}
    in_degree = {n: 0 for n in all_nodes}

    for a, b in edges:
        if b not in graph[a]:
            graph[a].add(b)
            in_degree[b] += 1
        if a == b:
            # self-loop counted, will be detected as cycle since it can't reduce to 0
            pass

    heap = [n for n in all_nodes if in_degree[n] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(result) != len(all_nodes):
        return None

    return result
