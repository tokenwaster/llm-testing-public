import os, sys
# Ensure the workspace root is on sys.path so that imports like 'toolkit' work.
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)
