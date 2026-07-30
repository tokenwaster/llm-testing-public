import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytest
sys.exit(pytest.main(["-v", "tests/test_collkit.py"]))
