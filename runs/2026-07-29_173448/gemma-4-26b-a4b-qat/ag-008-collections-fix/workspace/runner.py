import sys
import subprocess

sys.path.append('.')
subprocess.run([sys.executable, 'tests/test_collkit.py'])
