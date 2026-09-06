import subprocess, sys, os
sys.exit(subprocess.call([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-q"]))
