import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness tests
assert common_elements([1,2,3,2], [2,3,4]) == [2,3]
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(20) == 6765
assert count_pairs([1,2,3,2], 4) == 2  # (1,3) twice? Actually pairs: (1,3) at indices 0,2 and (2,2) at 1,3 => 2
# Let's compute manually: nums=[1,2,3,2], target=4
# pairs: (0,2)=4, (1,3)=4 =>2
assert dedupe_keep_order([1,2,1,3,2]) == [1,2,3]

print("Correctness OK")

# Timing tests
random.seed(0)
a = random.sample(range(1000000), 200000)
b = random.sample(range(1000000), 200000)
start = time.time()
common_elements(a,b)
print("common_elements time:", time.time()-start)

start = time.time()
fib(300)
print("fib(300) time:", time.time()-start)

nums = [random.randint(-10000,10000) for _ in range(100000)]
start = time.time()
count_pairs(nums, 0)
print("count_pairs time:", time.time()-start)

items = [random.randint(0,100000) for _ in range(200000)]
start = time.time()
dedupe_keep_order(items)
print("dedupe_keep_order time:", time.time()-start)
