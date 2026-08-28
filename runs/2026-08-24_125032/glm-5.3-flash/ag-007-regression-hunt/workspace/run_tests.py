import sys

try:
    import pytest
except ImportError:
    print("pytest not installed", file=sys.stderr)
    sys.exit(2)

sys.exit(pytest.main(["-v", "tests/test_toolkit.py"]))
