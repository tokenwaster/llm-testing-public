import sys
import pytest

sys.path.insert(0, ".")
raise SystemExit(pytest.main(["-q", "tests/test_toolkit.py"]))
