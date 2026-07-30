import sys
import pytest

sys.path.insert(0, ".")
raise SystemExit(pytest.main(["-v", "tests/test_collkit.py"]))
