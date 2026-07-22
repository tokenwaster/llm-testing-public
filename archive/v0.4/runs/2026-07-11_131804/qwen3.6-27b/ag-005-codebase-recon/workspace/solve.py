import importlib

current = "mod_27"  # START from entry.py
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    secret = mod.SECRET_TOKEN
    next_mod = mod.NEXT
    print(f"Step {i+1}: module={current}, SECRET_TOKEN={secret}, NEXT={next_mod}")
    if i == 6:
        print(f"\n7th module token: {secret}")
        with open("answer.txt", "w") as f:
            f.write(secret)
        break
    current = next_mod
