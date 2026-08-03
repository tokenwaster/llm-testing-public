#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_toolkit.py", "-v"], 
                       cwd=".")
sys.exit(result.returncode)
