import os

for fname in ['run_pytest.py', 'run_tests.py', 'debug_read.py']:
    if os.path.exists(fname):
        os.remove(fname)
