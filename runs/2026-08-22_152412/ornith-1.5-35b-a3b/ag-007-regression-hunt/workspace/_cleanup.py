import os
p = "_run_tests.py"
if os.path.exists(p):
    os.remove(p)
print("removed", p, "exists:", os.path.exists(p))
