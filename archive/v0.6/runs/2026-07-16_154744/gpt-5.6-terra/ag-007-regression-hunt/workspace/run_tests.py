"""Run the supplied test module with the workspace root on sys.path."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pytest

raise SystemExit(pytest.main(["-q", "tests/test_toolkit.py"]))
