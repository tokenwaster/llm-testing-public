import subprocess, sys
print(subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], capture_output=True, text=True).stdout)
