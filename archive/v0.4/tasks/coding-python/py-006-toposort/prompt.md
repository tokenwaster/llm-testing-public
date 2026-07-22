Write a function `topo_sort(edges: list[tuple[str, str]], nodes: list[str] | None = None) -> list[str] | None`.

- `edges` is a list of `(a, b)` pairs meaning **a must come before b**.
- `nodes`, if given, lists additional nodes that must appear in the output even
  if they have no edges. Nodes mentioned in `edges` are always included.
- Return a topological ordering of all nodes. When several orderings are valid,
  return the **lexicographically smallest** one (at every step, among all nodes
  currently available, pick the alphabetically first — i.e. Kahn's algorithm
  with a min-heap).
- If the graph contains a cycle, return `None`.
- Duplicate edges and self-loops may appear; a self-loop is a cycle.

Example: `topo_sort([("b","c"), ("a","c")])` returns `["a", "b", "c"]`.
