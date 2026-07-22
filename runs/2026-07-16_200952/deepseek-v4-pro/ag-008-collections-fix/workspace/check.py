import sys
sys.path.insert(0, '.')
from collkit import unique, partition, windows

print("unique:", unique([3, 1, 3, 2, 1]))
print("partition:", partition([1, 2, 3, 4], lambda x: x > 2))
print("windows:", windows([1, 2, 3, 4], 2))