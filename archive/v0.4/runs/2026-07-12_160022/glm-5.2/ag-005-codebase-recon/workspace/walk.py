import importlib

current = "mod_27"  # START
token = None
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(i + 1, current, token, "->", nxt)
    if i < 6:
        current = nxt

print("ANSWER:", token)
with open("answer.txt", "w") as f:
    f.write(token)
