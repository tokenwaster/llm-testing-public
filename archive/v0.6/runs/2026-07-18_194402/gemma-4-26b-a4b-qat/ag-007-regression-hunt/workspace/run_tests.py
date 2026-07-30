import unittest
import sys
import os

# Add current directory to sys.path to ensure toolkit is importable
sys.path.append(os.getcwd())

loader = unittest.TestLoader()
suite = loader.discover('tests')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    sys.exit(1)
