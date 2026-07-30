import importlib

import pipeline.entry as entry

current_mod_name = entry.START
print(f"1st (Start): {current_mod_name}")

for hop in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current_mod_name}")
    print(f"Hop {hop}: module {current_mod_name}, SECRET_TOKEN={mod.SECRET_TOKEN}, NEXT={mod.NEXT}")
    if hop == 7:
        secret = mod.SECRET_TOKEN
        print(f"\n7th module token: {secret}")
        with open("answer.txt", "w") as f:
            f.write(secret.strip())
        break
    current_mod_name = mod.NEXT
