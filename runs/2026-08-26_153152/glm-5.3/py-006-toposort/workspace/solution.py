import heapq


def topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None:
    # Gather all nodes: those appearing in edges plus any extra given nodes.
    node_set: set[str] = set(nodes) if nodes is not None else set()
    for a, b in edges:
        node_set.add(a)
        node_set.add(b)

    # Deduplicate edges so repeated edges don't clutter the graph
    # (they are harmless either way, but this keeps degrees clean).
    unique_edges = set(edges)

    indeg: dict[str, int] = {n: 0 for n in node_set}
    adj: dict[str, list[str]] = {n: [] for n in node_set}
    for a, b in unique_edges:
        adj[a].append(b)
        indeg[b] += 1

    # Kahn's algorithm with a min-heap: at every step, take the
    # alphabetically smallest node whose prerequisites are all emitted.
    heap = [n for n in node_set if indeg[n] == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        result.append(n)
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    # If some nodes were never emitted, the graph has a cycle
    # (self-loops included: such a node can never reach in-degree 0).
    if len(result) != len(node_set):
        return None
    return result
