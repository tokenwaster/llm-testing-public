import importlib, os

entry = importlib.import_module("pipeline.entry")
name = entry.START
chain = []
for i in range(7):
    m = importlib.import_module(f"pipeline.{name}")
    chain.append((i + 1, name, m.SECRET_TOKEN, m.NEXT))
    print(i + 1, name, m.SECRET_TOKEN, "->", m.NEXT)
    if i < 6:
        if m.NEXT is None:
            raise SystemExit("chain ended early")
        name = m.NEXT

token = chain[-1][2]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "answer.txt"), "w") as f:
    f.write(token)
print("ANSWER:", token)
