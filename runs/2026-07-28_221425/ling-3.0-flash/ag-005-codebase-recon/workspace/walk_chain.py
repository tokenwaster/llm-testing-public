import importlib

current = "pipeline.entry"
mod = importlib.import_module(current)
start = mod.START
print(f"START = {start}")

current_name = start
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current_name}")
    token = mod.SECRET_TOKEN
    next_name = mod.NEXT
    print(f"Step {i+1}: {current_name} -> SECRET_TOKEN={token}, NEXT={next_name}")
    if i == 6:
        # 7th module - write token to answer.txt
        with open("answer.txt", "w") as f:
            f.write(token)
        print(f"\nWrote token '{token}' to answer.txt")
    if next_name is None:
        print("Chain ended early!")
        break
    current_name = next_name