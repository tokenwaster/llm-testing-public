import subprocess
import sys

result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
print(f"Exit code: {result.returncode}")
