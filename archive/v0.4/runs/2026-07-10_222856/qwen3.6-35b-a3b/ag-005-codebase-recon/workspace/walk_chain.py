import importlib
import sys
sys.path.insert(0, '.')

current = "mod_27"
tokens = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    tokens.append((current, token))
    print(f"Step {i+1}: {current} -> SECRET_TOKEN = {token}")
    
    next_mod = mod.NEXT
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod

# Write the 7th module's token
with open("answer.txt", "w") as f:
    f.write(tokens[6][1])

print(f"\nAnswer written: {tokens[6][1]}")
