import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, "-m", "pytest", "tests/test_collkit.py", "-v"], cwd=os.path.dirname(os.path.abspath(__file__)))
