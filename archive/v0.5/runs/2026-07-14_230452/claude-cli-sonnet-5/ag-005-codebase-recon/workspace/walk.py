import re

name = "mod_27"
token = None
for i in range(7):
    with open(f"pipeline/{name}.py") as f:
        c = f.read()
    tok = re.search(r'SECRET_TOKEN\s*=\s*"([^"]*)"', c).group(1)
    nxt = re.search(r'NEXT\s*=\s*(None|"[^"]*")', c).group(1)
    print(i + 1, name, tok, nxt)
    token = tok
    if nxt == "None":
        break
    name = nxt.strip('"')

with open("answer.txt", "w") as f:
    f.write(token)
