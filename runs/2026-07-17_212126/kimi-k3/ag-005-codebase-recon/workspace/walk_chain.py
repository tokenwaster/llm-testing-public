"""Walk the pipeline chain for 7 modules starting from entry.START."""
import pipeline.entry as entry

current = entry.START
visited = []
for i in range(7):
    if current is None:
        raise RuntimeError(f"Chain ended early after {len(visited)} modules")
    mod = __import__(f"pipeline.{current}", fromlist=["NEXT", "SECRET_TOKEN"])
    visited.append((current, mod.SECRET_TOKEN))
    current = mod.NEXT

for i, (name, tok) in enumerate(visited, 1):
    print(f"{i}. {name} -> token={tok}")

seventh = visited[-1]
print(f"\n7th module: {seventh[0]}, token: {seventh[1]}")

with open("answer.txt", "w") as f:
    f.write(seventh[1])
print("Wrote answer.txt")
