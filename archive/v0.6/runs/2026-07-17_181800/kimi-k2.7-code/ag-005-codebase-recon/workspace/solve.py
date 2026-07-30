import importlib

module_name = "pipeline.entry"
entry = importlib.import_module(module_name)
start = entry.START
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
    current = next_mod
