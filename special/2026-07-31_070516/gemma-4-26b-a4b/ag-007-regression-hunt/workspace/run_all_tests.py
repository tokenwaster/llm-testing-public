import unittest
import sys
from io import StringIO

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    print(stream.getvalue())
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
