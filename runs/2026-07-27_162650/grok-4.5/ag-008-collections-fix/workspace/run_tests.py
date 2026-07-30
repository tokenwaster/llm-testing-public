import sys
sys.path.insert(0, ".")
import pytest
raise SystemExit(pytest.main(["-v", "tests/test_collkit.py"]))
