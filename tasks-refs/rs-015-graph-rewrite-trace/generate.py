import random
from collections import deque
from pathlib import Path

SEED = 150916
N_OPS = 300
TASK_ID = "rs-015-graph-rewrite-trace"
CATEGORY = "reasoning"

NAMES = [
    "ALDER", "BIRCH", "CEDAR", "DELTA", "EMBER", "FJORD", "GROVE", "HEATH",
    "INLET", "JETTY", "KNOLL", "LEDGE", "MARSH", "NORTH", "ORBIT", "PLAZA",
    "QUARRY", "RIDGE", "SHOAL", "TARN", "UPLAND", "VALE", "WHARF", "XENIA",
    "YARROW", "ZENITH", "ATLAS", "BASIN", "CAIRN", "DUNE", "ESKER", "FLATS",
    "GULCH", "HOLLOW", "ISLET", "JUNGLE", "KARST", "LAGOON", "MESA", "NOOK",
]

COMMENTS = [
    "# planned for next batch: ADD {a} -> {b}",
    "# reviewer note: consider DEL {a} -> {b} later",
    "# proposal (not applied): MERGE {a} INTO {b}",
    "# reminder: {a} may be renamed {b} in a future revision",
]


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def copy(self):
        g = Graph()
        g.nodes = set(self.nodes)
        g.edges = set(self.edges)
        return g

    def apply(self, op):
        kind = op[0]
        if kind == "ADD":
            _, a, b = op
            if a == b:
                return False
            self.nodes.update((a, b))
            self.edges.add((a, b))
            return True
        if kind == "DEL":
            _, a, b = op
            if (a, b) not in self.edges:
                return False
            self.edges.discard((a, b))
            return True
        if kind == "MERGE":
            _, x, y = op
            if x == y or x not in self.nodes or y not in self.nodes:
                return False
            new = set()
            for (a, b) in self.edges:
                a2 = y if a == x else a
                b2 = y if b == x else b
                if a2 != b2:
                    new.add((a2, b2))
            self.edges = new
            self.nodes.discard(x)
            return True
        if kind == "RENAME":
            _, x, z = op
            if x not in self.nodes or z in self.nodes:
                return False
            self.nodes.discard(x)
            self.nodes.add(z)
            self.edges = {(z if a == x else a, z if b == x else b)
                          for (a, b) in self.edges}
            return True
        raise ValueError(kind)


def replay(ops, cancelled):
    g = Graph()
    for i, op in enumerate(ops):
        if op[0] == "UNDO" or i in cancelled:
            continue
        g.apply(op)
    return g


def fmt(op):
    k = op[0]
    if k == "ADD":
        return f"ADD {op[1]} -> {op[2]}"
    if k == "DEL":
        return f"DEL {op[1]} -> {op[2]}"
    if k == "MERGE":
        return f"MERGE {op[1]} INTO {op[2]}"
    if k == "RENAME":
        return f"RENAME {op[1]} AS {op[2]}"
    return "UNDO"


def build():
    rng = random.Random(SEED)
    ops = []
    cancelled = set()
    live = Graph()
    retired = set()
    lines = []

    def pick_node():
        return rng.choice(sorted(live.nodes))

    def fresh_name():
        used = live.nodes | retired
        pool = [n for n in NAMES if n not in used]
        return rng.choice(pool) if pool else rng.choice(NAMES)

    for _ in range(N_OPS):
        r = rng.random()
        n_live = len(live.nodes)
        if n_live < 4 or r < 0.40:
            if n_live >= 2 and rng.random() < 0.55:
                a, b = rng.sample(sorted(live.nodes), 2)
                if rng.random() < 0.08:
                    b = a
            elif n_live >= 1 and rng.random() < 0.6:
                a, b = pick_node(), fresh_name()
                if rng.random() < 0.5:
                    a, b = b, a
            else:
                a, b = fresh_name(), fresh_name()
                while b == a:
                    b = fresh_name()
            op = ("ADD", a, b)
        elif r < 0.52:
            if live.edges and rng.random() < 0.75:
                a, b = rng.choice(sorted(live.edges))
            else:
                a, b = rng.sample(sorted(live.nodes), 2)
            op = ("DEL", a, b)
        elif r < 0.66:
            if rng.random() < 0.12 and retired:
                x, y = rng.choice(sorted(retired)), pick_node()
            else:
                x, y = rng.sample(sorted(live.nodes), 2)
            op = ("MERGE", x, y)
        elif r < 0.80:
            if rng.random() < 0.15 and retired:
                x = rng.choice(sorted(retired))
            else:
                x = pick_node()
            z = rng.choice(sorted(live.nodes)) if rng.random() < 0.12 \
                else (rng.choice(sorted(retired)) if retired and rng.random() < 0.3
                      else fresh_name())
            op = ("RENAME", x, z)
        else:
            op = ("UNDO",)

        if op[0] == "UNDO":
            target = None
            for i in range(len(ops) - 1, -1, -1):
                if ops[i][0] != "UNDO" and i not in cancelled:
                    target = i
                    break
            if target is not None:
                cancelled.add(target)
        ops.append(op)
        if rng.random() < 0.06 and len(live.nodes) >= 2:
            a, b = rng.sample(sorted(live.nodes), 2)
            lines.append(rng.choice(COMMENTS).format(a=a, b=b))
        lines.append(f"{len(ops):3d}. {fmt(op)}")
        before = set(live.nodes)
        live = replay(ops, cancelled)
        retired |= before - live.nodes
        retired -= live.nodes

    g = live
    nodes = sorted(g.nodes)
    out = {n: sorted(b for (a, b) in g.edges if a == n) for n in nodes}

    def reach(s):
        seen, dq = {s}, deque([s])
        while dq:
            u = dq.popleft()
            for v in out[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        return seen - {s}

    def shortest(s, t):
        dist, dq = {s: 0}, deque([s])
        while dq:
            u = dq.popleft()
            if u == t:
                return dist[u]
            for v in out[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    dq.append(v)
        return None

    def has_cycle():
        state = {}

        def dfs(u):
            state[u] = 1
            for v in out[u]:
                if state.get(v) == 1 or (state.get(v) is None and dfs(v)):
                    return True
            state[u] = 2
            return False
        return any(state.get(n) is None and dfs(n) for n in nodes)

    ranked = sorted(nodes, key=lambda n: (-len(reach(n)), n))
    src = ranked[0]
    targets = [n for n in nodes if n != src and shortest(src, n) is not None]
    far = sorted(targets, key=lambda n: (-shortest(src, n), n))
    dst = far[0] if far else [n for n in nodes if n != src][0]
    max_out = sorted(nodes, key=lambda n: (-len(out[n]), n))[0]
    answers = {
        "NUM_NODES": len(nodes),
        "NUM_EDGES": len(g.edges),
        "REACH_SRC": src,
        "REACHABLE": len(reach(src)),
        "PATH_DST": dst,
        "SHORTEST": shortest(src, dst) if shortest(src, dst) is not None else "NONE",
        "MAX_OUT_NODE": max_out,
        "MAX_OUT_DEGREE": len(out[max_out]),
        "HAS_CYCLE": "YES" if has_cycle() else "NO",
    }
    return "\n".join(lines), answers, len(cancelled)


PROMPT_TMPL = """A directed graph is built by applying the numbered operations
below, in order, starting from an empty graph (no nodes, no edges). Node names
are single uppercase words. Lines beginning with `#` are comments and do nothing.

Operations:

- `ADD a -> b` — creates `a` and `b` if they do not exist and adds the edge
  `a -> b` (no change if it already exists). If `a` and `b` are the same name,
  the operation is **ignored**.
- `DEL a -> b` — removes that edge if it exists (the nodes remain). If the edge
  does not exist, the operation is **ignored**.
- `MERGE x INTO y` — every edge `x -> n` becomes `y -> n` and every `n -> x`
  becomes `n -> y`; duplicates collapse; any edge that would become `y -> y` is
  dropped; `x` is removed. If `x` or `y` does not exist, or they are the same,
  the operation is **ignored**.
- `RENAME x AS z` — node `x` is now called `z` (its edges follow it). The old
  name `x` is free again and a later `ADD` may create a brand-new `x`. If `x`
  does not exist or `z` already exists, the operation is **ignored**.
- `UNDO` — cancels the most recent operation that is not an `UNDO` and has not
  already been cancelled. An ignored operation still counts as an operation:
  cancelling it consumes the `UNDO` and changes nothing. If nothing is left to
  cancel, the `UNDO` does nothing.

**The final graph is the result of applying, in their original order, every
operation that was never cancelled** (with the ignore rules evaluated in that
replay).

Answer about the final graph. End your reply with **exactly** these lines and
nothing after them:

```
NUM_NODES: <number of nodes>
NUM_EDGES: <number of edges>
REACHABLE: <number of nodes reachable from __SRC__ by following edges, not counting __SRC__ itself>
SHORTEST: <number of edges on a shortest directed path from __SRC__ to __DST__, or NONE>
MAX_OUT_NODE: <node with the most outgoing edges; ties -> alphabetically first>
MAX_OUT_DEGREE: <that node's outgoing edge count>
HAS_CYCLE: <YES if the final graph contains a directed cycle, else NO>
```

--- OPERATIONS ---

__BODY__
"""


CHECKER_TMPL = '''import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
__EXPECT__}


def _last(label):
    m = re.findall(rf"(?im)^\\s*\\**\\s*{label}\\s*\\**\\s*[:=]\\s*(.+?)\\s*$", TEXT)
    return m[-1].strip() if m else None


def _int(label):
    v = _last(label)
    if v is None:
        return None
    xs = re.findall(r"-?\\d+", v.replace(",", ""))
    return int(xs[0]) if xs else None


def _word(label):
    v = _last(label)
    if not v:
        return None
    m = re.search(r"[A-Z]{3,}", v.upper())
    return m.group(0) if m else None


def test_num_nodes():
    assert _int("NUM_NODES") == EXPECT["NUM_NODES"]


def test_num_edges():
    assert _int("NUM_EDGES") == EXPECT["NUM_EDGES"]


def test_reachable():
    assert _int("REACHABLE") == EXPECT["REACHABLE"]


def test_shortest():
    want = EXPECT["SHORTEST"]
    if want == "NONE":
        assert _word("SHORTEST") == "NONE"
    else:
        assert _int("SHORTEST") == want


def test_max_out_node():
    assert _word("MAX_OUT_NODE") == EXPECT["MAX_OUT_NODE"]


def test_max_out_degree():
    assert _int("MAX_OUT_DEGREE") == EXPECT["MAX_OUT_DEGREE"]


def test_has_cycle():
    assert _word("HAS_CYCLE") == EXPECT["HAS_CYCLE"]
'''


def render_checker(answers: dict) -> str:
    keep = {k: v for k, v in answers.items() if k not in ("REACH_SRC", "PATH_DST")}
    rows = "".join(
        f'    "{k}": ' + (f'"{v}"' if isinstance(v, str) else str(v)) + ",\n"
        for k, v in keep.items())
    return CHECKER_TMPL.replace("__EXPECT__", rows)


def main():
    body, answers, n_cancelled = build()
    prompt = (PROMPT_TMPL.replace("__SRC__", answers["REACH_SRC"])
              .replace("__DST__", answers["PATH_DST"])
              .replace("__BODY__", body))
    root = Path(__file__).resolve().parents[2]
    task_dir = root / "tasks" / CATEGORY / TASK_ID
    if not task_dir.is_dir():
        task_dir = root / "tasks-staging" / CATEGORY / TASK_ID
    task_dir.mkdir(parents=True, exist_ok=True)
    out = task_dir / "prompt.md"
    out.write_text(prompt, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(prompt):,} chars, {n_cancelled} ops cancelled)")
    chk = task_dir / "checker.py"
    chk.write_text(render_checker(answers), encoding="utf-8", newline="\n")
    print(f"wrote {chk} (answer key)")
    for k, v in answers.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
