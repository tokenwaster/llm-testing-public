import sys
import unittest

sys.path.insert(0, ".")

import tests.test_collkit as t

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(t)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
