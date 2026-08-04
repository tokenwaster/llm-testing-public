import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pipeline import entry

current = entry.START
print(f"Start: {current}")

for step in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(f"Step {step+1}: module={current}, token={token}, next={nxt}")
    if step == 6:
        print(f"\n7th module token: {token}")
        with open("answer.txt", "w") as f:
            f.write(token)
        break
    if nxt is None:
        print("Chain ended early!")
        break
    current = nxt