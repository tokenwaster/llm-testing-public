import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytest
if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", "tests/test_collkit.py"]))
