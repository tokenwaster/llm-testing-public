import subprocess
import sys
import os

env = os.environ.copy()
env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")

result = subprocess.run([sys.executable, "tests/test_toolkit.py"], env=env, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
