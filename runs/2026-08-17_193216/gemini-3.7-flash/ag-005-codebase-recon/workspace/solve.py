import importlib

import pipeline.entry as entry

current_mod_name = entry.START
visited = []

for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current_mod_name}")
    token = getattr(mod, "SECRET_TOKEN")
    next_mod = getattr(mod, "NEXT")
    print(f"Step {i}: module={current_mod_name}, token={token}, next={next_mod}")
    if i == 7:
        with open("answer.txt", "w") as f:
            f.write(token.strip())
        print(f"Saved 7th token: {token}")
    current_mod_name = next_mod
