import sys
sys.path.insert(0, '.')
import subprocess
result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_toolkit.py', '-v'], capture_output=False)
sys.exit(result.returncode)
