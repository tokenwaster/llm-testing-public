import ast, os, importlib, sys

PKG = "pipeline"
KEYS = ("NEXT", "SECRET_TOKEN", "START")

# --- Safe static walk: read constants without executing module code ---
info = {}
for fn in sorted(os.listdir(PKG)):
    if fn.endswith(".py") and fn != "__init__.py":
        name = fn[:-3]
        src = open(os.path.join(PKG, fn), encoding="utf-8").read()
        tree = ast.parse(src)
        vals = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in KEYS:
                        vals[t.id] = ast.literal_eval(node.value)
        info[name] = vals

start = info["entry"]["START"]
print("START =", start)

chain = []
cur = start
while cur is not None:
    chain.append(cur)
    cur = info[cur]["NEXT"]

print("chain (static):", chain)
seventh = chain[6]
print("7th module:", seventh, "->", info[seventh]["SECRET_TOKEN"])

# --- Cross-check by actually importing the modules ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
m = importlib.import_module(f"{PKG}.entry")
chain2 = []
cur = m.START
while cur is not None:
    chain2.append(cur)
    mod = importlib.import_module(f"{PKG}.{cur}")
    cur = mod.NEXT
print("chain (import):", chain2)
assert chain2 == chain, "static and import walks disagree!"

token = importlib.import_module(f"{PKG}.{seventh}").SECRET_TOKEN
assert token == info[seventh]["SECRET_TOKEN"]

# Write the bare token, no trailing newline
with open("answer.txt", "w", encoding="utf-8", newline="") as f:
    f.write(token)

# Verify what landed on disk
with open("answer.txt", "rb") as f:
    raw = f.read()
print("answer.txt bytes:", raw)
assert raw == token.encode(), "file content mismatch"
print("OK")
