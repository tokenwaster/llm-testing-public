import importlib
import pipeline.entry as entry

current = entry.START
chain = [current]
for i in range(6):  # follow 6 more hops to reach 7 total
    mod = importlib.import_module(f"pipeline.{current}")
    nxt = mod.NEXT
    if nxt is None:
        print(f"Chain ended at {current}, only visited {len(chain)} modules")
        break
    current = nxt
    chain.append(current)

print("Chain visited:", chain)
final_mod = importlib.import_module(f"pipeline.{current}")
print("7th module:", current)
print("SECRET_TOKEN:", final_mod.SECRET_TOKEN)

with open("answer.txt", "w") as f:
    f.write(final_mod.SECRET_TOKEN)

# Verify
with open("answer.txt") as f:
    print("answer.txt contents:", repr(f.read()))