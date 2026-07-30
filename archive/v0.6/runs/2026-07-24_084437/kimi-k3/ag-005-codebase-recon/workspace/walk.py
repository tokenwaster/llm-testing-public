"""Walk the pipeline dispatch chain for 7 hops and report the 7th module's token."""
import importlib

from pipeline.entry import START

current = START
visited = []
token = None
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    token = mod.SECRET_TOKEN
    current = mod.NEXT

print("Chain:", " -> ".join(visited))
print("7th module:", visited[-1])
print("Token:", token)

with open("answer.txt", "w") as f:
    f.write(token)
