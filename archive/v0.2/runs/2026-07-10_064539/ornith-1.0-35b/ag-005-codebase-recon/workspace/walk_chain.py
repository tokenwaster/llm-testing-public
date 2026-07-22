import importlib, sys
sys.path.insert(0, '.')

start = "mod_27"
current = start
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    print(f"{i}: {current} -> SECRET_TOKEN={token}, NEXT={mod.NEXT}")
    if i == 7:
        with open("answer.txt", "w") as f:
            f.write(token)
        break
    current = mod.NEXT
