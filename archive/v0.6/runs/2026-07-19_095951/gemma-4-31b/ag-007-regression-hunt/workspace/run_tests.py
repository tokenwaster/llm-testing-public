import sys
import os
import pytest

# Ensure the current directory is in the path so 'toolkit' can be found
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    # Run pytest on the test file
    sys.exit(pytest.main(["tests/test_toolkit.py"]))
