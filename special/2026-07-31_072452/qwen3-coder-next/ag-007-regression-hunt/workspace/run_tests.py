import sys
sys.path.insert(0, '.')
import subprocess

result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
print("Exit code:", result.returncode)
