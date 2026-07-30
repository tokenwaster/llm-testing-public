import subprocess
import sys

result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_collkit.py', '-v'], cwd='.')
sys.exit(result.returncode)
