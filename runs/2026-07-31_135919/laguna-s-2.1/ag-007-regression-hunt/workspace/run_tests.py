import sys
import os

# Add workspace root to path so 'toolkit' is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest

if __name__ == "__main__":
    sys.exit(pytest.main(["tests/test_toolkit.py", "-v"]))
