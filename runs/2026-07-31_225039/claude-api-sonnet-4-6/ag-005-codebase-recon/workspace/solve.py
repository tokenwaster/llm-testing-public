import importlib

# Load entry to get START
import pipeline.entry as entry
current = entry.START
print(f"START: {current}")

for hop in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    next_mod = mod.NEXT
    print(f"Hop {hop}: {current} -> SECRET_TOKEN={token}, NEXT={next_mod}")
    if hop == 7:
        print(f"\n7th module: {current}, SECRET_TOKEN: {token}")
        with open("answer.txt", "w") as f:
            f.write(token)
        break
    current = next_mod
