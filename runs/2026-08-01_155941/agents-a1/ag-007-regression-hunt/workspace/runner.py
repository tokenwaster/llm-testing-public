import sys
import os

# Add workspace root to Python path so toolkit imports work
sys.path.insert(0, os.getcwd())

try:
    import pytest
except ImportError as e:
    print(f"pytest not available: {e}")
    # Try using subprocess with python -m pytest? Not sure if that will inherit sys.path.
    exit(1)

# Run pytest on the test file
exit_code = pytest.main(['-v', 'tests/test_toolkit.py'])
sys.exit(exit_code)
