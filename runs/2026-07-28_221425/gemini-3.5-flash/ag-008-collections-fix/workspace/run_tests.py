import pytest
import sys

# Add current directory to path so pytest can find collkit
sys.path.insert(0, ".")

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "tests/test_collkit.py"]))
