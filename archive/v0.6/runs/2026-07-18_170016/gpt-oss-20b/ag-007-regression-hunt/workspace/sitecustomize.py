import os, sys
# Ensure current directory and its parent are on sys.path
for path in [os.getcwd(), os.path.abspath(os.path.join(os.getcwd(),'..'))]:
    if path not in sys.path:
        sys.path.insert(0,path)
