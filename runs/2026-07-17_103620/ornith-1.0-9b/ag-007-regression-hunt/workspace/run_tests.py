import os
import sys

# Add the workspace root to path so toolkit is importable as a package
workspace_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, workspace_root)
print(f"Adding {workspace_root} to sys.path")
print(f"toolkit exists: {os.path.exists(os.path.join(workspace_root, 'toolkit'))}")

# Import toolkit as a package
import toolkit
from toolkit.dates import days_in_month, is_leap_year
from toolkit.stats import mean, median, mode_of
from toolkit.text import snake_case, title_case, truncate

print("All imports successful!")

# Run all test functions from the test file
import tests.test_toolkit as tt
tests = [obj for name, obj in vars(tt).items() if name.startswith("test_")]
passed = 0
failed = 0
for t in sorted(tests, key=lambda x: x.__name__):
    try:
        t()
        passed += 1
        print(f"PASS {t.__name__}")
    except Exception as e:
        failed += 1
        import traceback
        traceback.print_exc()
        print(f"FAIL {t.__name__}: {e}")

print(f"\n{passed} passed, {failed} failed")