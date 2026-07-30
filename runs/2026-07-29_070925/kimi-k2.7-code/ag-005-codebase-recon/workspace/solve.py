import importlib

module_name = "pipeline.entry"
mod = importlib.import_module(module_name)
start = getattr(mod, "START")
module_name = "pipeline." + start
visited = []
for i in range(7):
    mod = importlib.import_module(module_name)
    visited.append(module_name)
    if i == 6:
        print(getattr(mod, "SECRET_TOKEN", None))
        break
    nxt = getattr(mod, "NEXT", None)
    if nxt is None:
        print("chain ended early", visited)
        break
    module_name = "pipeline." + nxt
