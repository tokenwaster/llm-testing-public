import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_collkit.py", "-v"], capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
print("exit", r.returncode)
