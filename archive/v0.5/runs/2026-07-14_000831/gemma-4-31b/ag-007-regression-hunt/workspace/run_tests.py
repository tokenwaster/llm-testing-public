import sys
import os

# Add current directory to path so 'toolkit' can be found
sys.path.append(os.getcwd())

import pytest

if __name__ == "__main__":
    # Run pytest on the test file
    sys.exit(pytest.main(["tests/test_toolkit.py"]))
