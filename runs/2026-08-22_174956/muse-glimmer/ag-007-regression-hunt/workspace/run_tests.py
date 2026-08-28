import subprocess, sys
sys.exit(subprocess.call([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"]))
