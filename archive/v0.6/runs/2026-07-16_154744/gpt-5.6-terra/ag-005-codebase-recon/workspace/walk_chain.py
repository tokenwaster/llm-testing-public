"""Resolve the requested seven-module dispatch chain."""
import importlib

start = importlib.import_module("pipeline.entry").START
name = start
visited = []
for _ in range(7):
    module = importlib.import_module(f"pipeline.{name}")
    visited.append(name)
    token = module.SECRET_TOKEN
    name = module.NEXT

assert len(visited) == 7
assert token
print(" -> ".join(visited))
print(token)
with open("answer.txt", "w", encoding="utf-8") as output:
    output.write(token)
