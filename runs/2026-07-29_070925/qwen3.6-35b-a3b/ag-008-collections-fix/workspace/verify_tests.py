import sys
sys.path.insert(0, '.')

from collkit import chunk, flatten, group_by, partition, take_while, unique, windows

passed = 0
failed = 0

def check(name, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name}: got {actual!r}, expected {expected!r}")

print("test_chunk:")
check("basic", chunk([1,2,3,4,5], 2), [[1,2],[3,4],[5]])
check("empty", chunk([], 3), [])
try:
    chunk([1], 0)
    check("error", "no error", "ValueError")
except ValueError:
    passed += 1
    print("  PASS value_error")

print("\ntest_flatten:")
check("basic", flatten([1,[2,3],[4],5]), [1,2,3,4,5])
check("strings", flatten(["ab",["c"]]), ["ab","c"])

print("\ntest_group_by:")
check("grouped", group_by([1,2,3,4], lambda x: x%2), {1:[1,3],0:[2,4]})

print("\ntest_take_while:")
check("evens", take_while([2,4,5,6], lambda x: x%2==0), [2,4])
check("none", take_while([1,2], lambda x: x>5), [])

print("\ntest_unique_values:")
check("sorted", sorted(unique([3,1,3,2,1])), [1,2,3])

print("\ntest_partition_union:")
y, n = partition([1,2,3,4], lambda x: x > 2)
check("union", sorted(y+n), [1,2,3,4])

print("\ntest_windows_first:")
check("first", windows([1,2,3,4], 2)[0], [1,2])

print("\ntest_unique_order:")
check("order", unique([3,1,3,2,1]), [3,1,2])

print("\ntest_partition_orientation:")
y, n = partition([1,2,3,4], lambda x: x > 2)
check("orient", (y==[3,4] and n==[1,2]), True)

print("\ntest_windows_complete:")
check("complete", windows([1,2,3,4], 2), [[1,2],[2,3],[3,4]])

print(f"\n{passed}/{passed+failed} tests passed")
