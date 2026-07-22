import subprocess
import sys

def run_tests():
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py"], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)

if __name__ == "__main__":
    run_tests()
