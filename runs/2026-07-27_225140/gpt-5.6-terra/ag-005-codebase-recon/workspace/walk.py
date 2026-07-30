import importlib
from pipeline.entry import START

name = START
chain = []
for _ in range(7):
    module = importlib.import_module(f"pipeline.{name}")
    chain.append((name, module.SECRET_TOKEN))
    name = module.NEXT
print(chain)
with open("answer.txt", "w", encoding="utf-8") as f:
    f.write(chain[-1][1])
