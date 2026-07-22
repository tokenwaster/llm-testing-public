import importlib

# Start from entry.py's START
from pipeline.entry import START

current = START
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    if i == 6:  # 7th module (0-indexed: 6)
        print(f"7th module: {current}")
        print(f"SECRET_TOKEN: {mod.SECRET_TOKEN}")
        with open("answer.txt", "w") as f:
            f.write(mod.SECRET_TOKEN)
        break
    current = mod.NEXT
    print(f"Step {i+1}: {current}")
