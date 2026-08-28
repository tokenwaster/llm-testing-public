import sys
import pathlib
# Ensure the workspace root is on sys.path
root = pathlib.Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
sys.exit(pytest.main(["-q"]))
