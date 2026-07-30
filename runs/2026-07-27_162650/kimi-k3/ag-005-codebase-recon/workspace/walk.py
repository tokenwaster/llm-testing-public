import importlib
import pipeline.entry as entry

current = entry.START
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    print(f"hop {i}: {current} NEXT={mod.NEXT}")
    if i == 7:
        token = mod.SECRET_TOKEN
        print("7th module token:", token)
        with open("answer.txt", "w") as f:
            f.write(token)
    current = mod.NEXT
