import subprocess, sys
result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], capture_output=False)
