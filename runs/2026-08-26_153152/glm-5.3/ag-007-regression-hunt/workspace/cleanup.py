import os
for f in ("run_tests.py", "check_edges.py"):
    if os.path.exists(f):
        os.remove(f)
print("cleaned up helper scripts")
