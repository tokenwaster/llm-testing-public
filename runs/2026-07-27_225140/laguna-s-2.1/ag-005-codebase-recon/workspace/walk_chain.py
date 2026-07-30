import importlib

import pipeline.entry as entry

chain = []
current = entry.START
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    chain.append((current, mod.SECRET_TOKEN, mod.NEXT))
    print(f"Step {i+1}: module={current}, SECRET_TOKEN={mod.SECRET_TOKEN}, NEXT={mod.NEXT}")
    current = mod.NEXT

print()
print(f"7th module: {chain[6][0]}")
print(f"7th SECRET_TOKEN: {chain[6][1]}")
