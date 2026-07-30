import importlib

# Let's inspect pipeline.entry first
import pipeline.entry
start = getattr(pipeline.entry, "START", None)
print(f"START is {start}")

current = start
history = []
for i in range(1, 11): # Let's find at least 10 in the chain
    if current is None:
        print(f"Reached end of chain at step {i-1}")
        break
    mod = importlib.import_module(f"pipeline.{current}")
    next_mod = getattr(mod, "NEXT", None)
    token = getattr(mod, "SECRET_TOKEN", None)
    history.append((current, token))
    print(f"Step {i}: {current} -> SECRET_TOKEN: {token}, NEXT: {next_mod}")
    current = next_mod
