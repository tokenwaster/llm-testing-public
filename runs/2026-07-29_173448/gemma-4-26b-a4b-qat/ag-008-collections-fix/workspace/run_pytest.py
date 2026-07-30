import subprocess
import sys

def run_pytest():
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_collkit.py"], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_pytest())
