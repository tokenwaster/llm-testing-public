import importlib

start = importlib.import_module("pipeline.entry").START
name = start
for i in range(7):
    mod = importlib.import_module(f"pipeline.{name}")
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(f"{i+1}: {name} token={token} NEXT={nxt}")
    name = nxt
