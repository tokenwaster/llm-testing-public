import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], capture_output=True, text=True)
print(r.stdout)
if r.returncode != 0:
    print("STDERR:", r.stderr)
print("EXIT:", r.returncode)