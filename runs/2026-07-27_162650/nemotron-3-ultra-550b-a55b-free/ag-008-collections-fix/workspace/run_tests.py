import sys
sys.path.insert(0, '.')

import pytest

# Run the tests
pytest.main(['tests/test_collkit.py', '-v'])