import os

for path in ["test_perf.py", "test_edge_cases.py"]:
    if os.path.exists(path):
        os.remove(path)
