import pytest
import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath("."))
    ret = pytest.main(["-v", "tests/test_toolkit.py"])
    sys.exit(ret)
