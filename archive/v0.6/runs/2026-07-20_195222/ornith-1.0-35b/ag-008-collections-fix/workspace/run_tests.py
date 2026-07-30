import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytest
pytest.main([os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "test_collkit.py"), "-v"])
