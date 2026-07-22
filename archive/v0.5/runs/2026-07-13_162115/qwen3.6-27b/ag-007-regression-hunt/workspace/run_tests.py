import sys
import os

# Add workspace root to path so 'toolkit' package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
sys.exit(pytest.main([os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"), "-v"]))
