import sys
import os

# Add workspace root to path so collkit is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
sys.exit(pytest.main(['tests/test_collkit.py', '-v']))
