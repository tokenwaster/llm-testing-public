import subprocess
import sys

def main():
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py"], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            sys.exit(result.returncode)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
