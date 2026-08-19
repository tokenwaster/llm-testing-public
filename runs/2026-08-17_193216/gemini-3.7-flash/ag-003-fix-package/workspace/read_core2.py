with open("textstats/core.py", "r") as f:
    for i, line in enumerate(f):
        print(f"{i+1}: {line}", end="")
