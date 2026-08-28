import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_collkit.py", "-v"],
                   cwd=".")
sys.exit(r.returncode)
