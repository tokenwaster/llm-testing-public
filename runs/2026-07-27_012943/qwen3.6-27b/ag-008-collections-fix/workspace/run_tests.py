import sys
import os
sys.path.insert(0, os.getcwd())
import pytest
sys.exit(pytest.main(['tests/test_collkit.py', '-v']))
