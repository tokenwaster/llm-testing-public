import sys
import os
import pytest

sys.path.append(os.getcwd())

# Run pytest on the test file
ret = pytest.main(["tests/test_toolkit.py"])
sys.exit(ret)
