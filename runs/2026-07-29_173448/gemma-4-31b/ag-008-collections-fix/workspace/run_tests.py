import sys
import os
sys.path.append(os.getcwd())
import pytest

if __name__ == "__main__":
    pytest.main(["tests/test_collkit.py"])
