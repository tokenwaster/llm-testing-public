import sys
import os
import subprocess

# Add current directory to sys.path
sys.path.append(os.getcwd())

import unittest
import importlib

# We need to make sure toolkit is importable.
# Since we are running this script, the current directory is already in sys.path.

import tests.test_toolkit as test_toolkit

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_toolkit)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
