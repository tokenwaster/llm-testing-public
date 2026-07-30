import sys
sys.path.insert(0, '.')

# Import test module and run tests manually
import pytest
exit_code = pytest.main(['-v', 'tests/test_toolkit.py'])
print(f"\nExit code: {exit_code}")