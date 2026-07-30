import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pytest
pytest.main(["-v", "tests/test_toolkit.py"])
