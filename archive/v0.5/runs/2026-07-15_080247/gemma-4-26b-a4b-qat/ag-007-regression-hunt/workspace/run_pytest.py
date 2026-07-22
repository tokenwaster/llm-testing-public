import pytest
import sys
import os

# Add current directory to sys.path so toolkit can be found
sys.path.append(os.getcwd())

# Run pytest on the test file
sys.exit(pytest.main(["tests/test_toolkit.py"]))
