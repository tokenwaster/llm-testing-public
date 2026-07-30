import pytest
import sys
from collkit import (chunk, flatten, group_by, partition, take_while, unique,
                     windows)

# This is a trick to run pytest from here if needed
# but actually I can just try running it as a module.
if __name__ == "__main__":
    pytest.main(["tests/test_collkit.py"])
