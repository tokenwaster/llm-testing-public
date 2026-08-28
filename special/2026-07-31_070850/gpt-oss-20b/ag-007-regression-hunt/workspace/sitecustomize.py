import sys, os
# Ensure the repository root is on sys.path so that imports like 'toolkit' work when
# running from a subdirectory (e.g., tests/). This file is automatically imported by
# Python's site module during interpreter start-up.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
