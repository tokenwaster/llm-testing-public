import importlib

current = "mod_27"
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    print(f"{i+1}: {current} SECRET_TOKEN={mod.SECRET_TOKEN} NEXT={mod.NEXT}")
    current = mod.NEXT
