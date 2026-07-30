import importlib, sys
from pipeline.entry import START

current = START
tokens = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    tokens.append((current, token))
    print(f"{i+1}: {current} -> SECRET_TOKEN={token}, NEXT={mod.NEXT}")
    current = mod.NEXT

with open("answer.txt", "w") as f:
    f.write(tokens[6][1])
print("\nAnswer written:", tokens[6][1])
