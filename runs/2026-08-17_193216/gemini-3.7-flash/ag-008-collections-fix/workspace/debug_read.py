import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with open('collkit.py', 'r') as f:
    print("=== collkit.py ===")
    print(f.read())

with open('tests/test_collkit.py', 'r') as f:
    print("=== tests/test_collkit.py ===")
    print(f.read())
