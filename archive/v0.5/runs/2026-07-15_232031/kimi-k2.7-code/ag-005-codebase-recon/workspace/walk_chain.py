import importlib

start_module = "pipeline.entry"
mod = importlib.import_module(start_module)
start = mod.START
print(f"START: {start}")

current = start
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    next_mod = mod.NEXT
    print(f"{i}: {current} -> token={token}, NEXT={next_mod}")
    if i == 7:
        with open("answer.txt", "w") as f:
            f.write(token)
        print(f"Wrote token of 7th module ({current}) to answer.txt")
        break
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod
