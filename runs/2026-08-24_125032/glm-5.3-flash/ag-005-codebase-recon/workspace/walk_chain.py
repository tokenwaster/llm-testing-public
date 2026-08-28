import importlib

mod = importlib.import_module("pipeline.entry")
current = mod.START
print(f"START -> {current}")

visited = []
for i in range(7):
    m = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    token = getattr(m, "SECRET_TOKEN", None)
    nxt = getattr(m, "NEXT", None)
    print(f"{i+1:2d}. {current}: NEXT={nxt!r}, SECRET_TOKEN={token!r}")
    if i < 6:
        if nxt is None:
            raise SystemExit("Chain ended early!")
        current = nxt

seventh = visited[6]
m7 = importlib.import_module(f"pipeline.{seventh}")
token7 = m7.SECRET_TOKEN
print(f"\n7th module: {seventh}")
print(f"Token: {token7}")

with open("answer.txt", "w") as f:
    f.write(token7)
