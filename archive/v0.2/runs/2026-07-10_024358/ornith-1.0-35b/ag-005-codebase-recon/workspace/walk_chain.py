import importlib
import sys
sys.path.insert(0, '.')

start = "mod_27"
current = start
tokens = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    tokens.append(mod.SECRET_TOKEN)
    print(f"{i+1}: {current} -> SECRET_TOKEN={mod.SECRET_TOKEN}, NEXT={mod.NEXT}")
    current = mod.NEXT

with open("answer.txt", "w") as f:
    f.write(tokens[6])
