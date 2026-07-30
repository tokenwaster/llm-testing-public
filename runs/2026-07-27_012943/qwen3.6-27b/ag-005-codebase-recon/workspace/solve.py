import importlib

visited = []
current = "mod_27"

for i in range(7):
    visited.append(current)
    mod = importlib.import_module(f"pipeline.{current}")
    print(f"#{i+1}: {current} -> NEXT={mod.NEXT}, SECRET_TOKEN={mod.SECRET_TOKEN}")
    if mod.NEXT is None:
        print("Chain ended before 7 modules!")
        break
    current = mod.NEXT

# The 7th module's token is what we need
print(f"\n7th module: {visited[6]}")
print(f"Token: {mod.SECRET_TOKEN}")

with open("answer.txt", "w") as f:
    f.write(mod.SECRET_TOKEN)

print("Written to answer.txt")
