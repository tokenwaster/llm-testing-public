import sys, os
print('cwd', os.getcwd())
print('sys.path', sys.path)
try:
    import toolkit
    print('toolkit imported', toolkit.__file__)
except Exception as e:
    print('error', e)
