import pytest
import sys
import os

# Add current directory to sys.path so toolkit can be found
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    # Use pytest.main directly in a script
    retcode = pytest.main(["tests/test_toolkit.py"])
    sys.exit(retcode)
