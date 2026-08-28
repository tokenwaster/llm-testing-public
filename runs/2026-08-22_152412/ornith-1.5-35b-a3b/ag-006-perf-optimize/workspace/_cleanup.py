import os
for f in ["_test.py", "_correct.py"]:
    if os.path.exists(f):
        os.remove(f)
print("cleaned")
