import sys
sys.path.insert(0, '.')  # Add current directory to path so collkit is found in tests/...

import pytest

exit_code = pytest.main(['-xvs', 'tests/test_collkit.py'])
print(f"pytest exit code: {exit_code}")
sys.exit(exit_code)
