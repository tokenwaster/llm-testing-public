import subprocess
import sys

result = subprocess.run([sys.executable, "-m", "unittest", "tests/test_collkit.py"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
exit(result.returncode)
