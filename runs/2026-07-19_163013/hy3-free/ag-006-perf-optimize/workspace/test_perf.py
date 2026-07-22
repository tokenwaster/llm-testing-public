import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# correctness checks
assert common_elements([3,1,2,1], [2,3,4]) == [2,3]
assert fib(0)==0 and fib(1)==1 and fib(10)==55 and fib(20)==6765
assert count_pairs([1,2,3,4,3], 6) == 2  # (2,4),(3,3)
assert dedupe_keep_order([1,2,2,3,1,4]) == [1,2,3,4]

# timing
random.seed(0)
a = [random.randint(0, 100000) for _ in range(200000)]
b = [random.randint(0, 100000) for _ in range(200000)]
t=time.time(); common_elements(a,b); print("common_elements", time.time()-t)

t=time.time(); print("fib(300)=", fib(300)); print("fib time", time.time()-t)

nums = [random.randint(0, 100000) for _ in range(100000)]
t=time.time(); print("count_pairs", count_pairs(nums, 50000)); print("count_pairs time", time.time()-t)

items = [random.randint(0, 100000) for _ in range(200000)]
t=time.time(); dedupe_keep_order(items); print("dedupe time", time.time()-t)
print("ALL OK")
