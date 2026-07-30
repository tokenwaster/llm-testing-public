import sys
import os

# Add current directory to path so collkit can be found
sys.path.append(os.getcwd())

import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main(["tests/test_collkit.py"]))
