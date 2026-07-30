import sys
sys.path.insert(0, '.')
import subprocess
subprocess.run([sys.executable, '-m', 'pytest', '-v', 'tests/test_toolkit.py'])
