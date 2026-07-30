import sys
sys.path.insert(0, '.')
import pytest
sys.exit(pytest.main(['tests/test_toolkit.py', '-v']))
