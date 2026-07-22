import sys
import os
import unittest

# Add current directory to sys.path
sys.path.insert(0, os.getcwd())

# Import the test module
try:
    import tests.test_toolkit as test_module
    suite = unittest.TestLoader().loadTestsFromModule(test_module)
    unittest.TextTestRunner().run(suite)
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Exception: {e}")
