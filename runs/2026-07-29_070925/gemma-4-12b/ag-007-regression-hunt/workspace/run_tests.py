import sys
import os

sys.path.append(os.getcwd())

import pytest
import tests.test_toolkit as test_suite

if __name__ == "__main__":
    pytest.main(["tests/test_toolkit.py"])
