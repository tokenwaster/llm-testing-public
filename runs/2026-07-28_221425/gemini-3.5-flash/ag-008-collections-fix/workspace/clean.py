import os

for f in ['helper.py', 'run_tests.py']:
    if os.path.exists(f):
        os.remove(f)
