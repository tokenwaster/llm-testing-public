import sys
import os
import subprocess

sys.path.append(os.getcwd())
import unittest
import tests.test_collkit as test_module

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
