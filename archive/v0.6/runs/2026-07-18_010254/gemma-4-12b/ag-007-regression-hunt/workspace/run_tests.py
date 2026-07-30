import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# The toolkit is in the parent directory of tests/ if we are running from tests/, 
# but here it seems to be at the same level as tests/.
# Let's check current directory contents again.

# Current dir:
# tests/test_toolkit.py
# toolkit/__init__.py
# ...

sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    pytest.main(["tests/test_toolkit.py"])
