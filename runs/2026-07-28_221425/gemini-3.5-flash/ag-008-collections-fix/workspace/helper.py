import sys
import os

print("Files in workspace:", os.listdir('.'))

with open('collkit.py', 'r') as f:
    print("--- collkit.py ---")
    print(f.read())

with open('tests/test_collkit.py', 'r') as f:
    print("--- tests/test_collkit.py ---")
    print(f.read())
