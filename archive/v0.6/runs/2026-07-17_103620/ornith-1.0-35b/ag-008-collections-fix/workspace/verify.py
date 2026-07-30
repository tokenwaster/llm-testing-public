"""Quick verification of the three bugfixes."""
from collkit import unique, partition, windows

# Test 1: unique order preservation
assert unique([3, 1, 3, 2, 1]) == [3, 1, 2], f"got {unique([3, 1, 3, 2, 1])}"

# Test 2: partition orientation (matches first)
y, n = partition([1, 2, 3, 4], lambda x: x > 2)
assert y == [3, 4] and n == [1, 2], f"got y={y}, n={n}"

# Test 3: windows complete (includes last window)
assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]], f"got {windows([1, 2, 3, 4], 2)}"

print("All three fixes verified!")
