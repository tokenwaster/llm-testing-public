import subprocess, sys, os
r = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_toolkit.py', '-p', 'no:cacheprovider'], capture_output=True, text=True, cwd=os.path.dirname(__file__) or '.')
print('RC:', r.returncode)
print('STDOUT:'); print(r.stdout)
print('STDERR:'); print(r.stderr)
