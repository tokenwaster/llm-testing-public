import sys
import pathlib
root = pathlib.Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
sys.exit(pytest.main(["-q"]))
