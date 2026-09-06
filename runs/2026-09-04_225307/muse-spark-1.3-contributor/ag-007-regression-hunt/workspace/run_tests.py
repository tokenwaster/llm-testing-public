import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
print("RC", r.returncode)
