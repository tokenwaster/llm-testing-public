import subprocess
import sys

res = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
print("Exit code:", res.returncode)
