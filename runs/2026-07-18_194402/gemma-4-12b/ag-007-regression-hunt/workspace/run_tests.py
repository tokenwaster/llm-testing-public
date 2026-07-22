import sys
import os
import pytest

# Add the current directory to the path so 'toolkit' can be imported
sys.path.append(os.getcwd())

# Run the tests
if __name__ == "__main__":
    pytest.main(["tests/test_toolkit.py"])
