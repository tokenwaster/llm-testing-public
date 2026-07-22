import subprocess
import sys
import os

# Add current directory to PYTHONPATH
os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

try:
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py"], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
except Exception as e:
    print(e)
    sys.exit(1)
