import sys
import os

# Add current directory to path so toolkit can be imported
sys.path.insert(0, os.getcwd())

import pytest

if __name__ == "__main__":
    # Run the tests in tests/test_toolkit.py
    sys.exit(pytest.main(["tests/test_toolkit.py"]))
