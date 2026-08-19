import importlib

name = "mod_27"
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{name}")
    print(i, name, mod.SECRET_TOKEN, "NEXT=", mod.NEXT)
    name = mod.NEXT
