import importlib

import pipeline.entry as entry

current = entry.START
visited = [current]
for i in range(6):  # need to reach the 7th module
    mod = importlib.import_module(f"pipeline.{current}")
    nxt = mod.NEXT
    if nxt is None:
        raise RuntimeError("Chain ended early")
    current = nxt
    visited.append(current)

final = importlib.import_module(f"pipeline.{current}")
print("Visited:", visited)
print("7th module:", current)
print("SECRET_TOKEN:", final.SECRET_TOKEN)
