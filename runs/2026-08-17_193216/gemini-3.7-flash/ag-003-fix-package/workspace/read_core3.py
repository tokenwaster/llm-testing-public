import reprlib
with open("textstats/core.py", "r") as f:
    text = f.read()
for line in text.splitlines():
    print(repr(line))
