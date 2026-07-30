import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
sys.exit(pytest.main([os.path.join(os.path.dirname(__file__), 'tests', 'test_collkit.py'), '-v']))
