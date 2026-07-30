import sys
import os
sys.path.append(os.path.abspath('.'))
from tests.test_toolkit import *
import pytest

if __name__ == "__main__":
    pytest.main([__file__])
