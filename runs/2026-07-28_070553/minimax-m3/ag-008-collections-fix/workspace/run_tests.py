import subprocess, sys
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_collkit.py", "-v"],
    capture_output=True, text=True,
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("EXIT:", result.returncode)