import importlib

import pipeline.entry as entry

current_name = entry.START
print(f"Start module name: {current_name}")

visited = []

for hop in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current_name}")
    token = getattr(mod, "SECRET_TOKEN")
    next_mod = getattr(mod, "NEXT")
    print(f"Hop {hop}: module={current_name}, token={token}, next={next_mod}")
    visited.append((hop, current_name, token))
    current_name = next_mod

seventh_token = visited[6][2]
print(f"\n7th module token: {seventh_token}")

with open("answer.txt", "w") as f:
    f.write(str(seventh_token).strip() + "\n")
