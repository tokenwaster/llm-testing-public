import importlib

import pipeline
import pipeline.entry as entry

current = entry.START
print(f"Start: {current}")

for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    token = getattr(mod, "SECRET_TOKEN")
    nxt = getattr(mod, "NEXT")
    print(f"Step {i}: {current} -> token={token}, NEXT={nxt}")
    if i == 7:
        # This is the 7th module
        with open("answer.txt", "w") as f:
            f.write(token + "\n")
        print(f"WROTE ANSWER: {token}")
        break
    if nxt is None:
        print("Chain ended early")
        break
    current = nxt
