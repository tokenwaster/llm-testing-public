import time
import random
import perf

# correctness checks
import itertools

# common_elements
a = [3,1,2,3,4,5]
b = [4,5,6,1,1]
assert perf.common_elements(a,b) == sorted(set(a)&set(b)), perf.common_elements(a,b)

# fib
assert perf.fib(0)==0 and perf.fib(1)==1 and perf.fib(10)==55 and perf.fib(20)==6765 and perf.fib(300)==222232244629420445529739893461909967206666939096499764990979600

# count_pairs brute
random.seed(1)
nums = [random.randint(0,50) for _ in range(2000)]
target = 30
c = perf.count_pairs(nums, target)
brute = sum(1 for i in range(len(nums)) for j in range(i+1,len(nums)) if nums[i]+nums[j]==target)
assert c==brute, (c,brute)

# dedupe
items = [1,2,3,2,4,1,5,3]
assert perf.dedupe_keep_order(items)==[1,2,3,4,5]

# timing
t=time.time(); perf.common_elements(list(range(200000)), list(range(100000,300000))); assert time.time()-t<2
t=time.time(); perf.fib(300); assert time.time()-t<2
random.seed(2); big=[random.randint(0,1000) for _ in range(100000)]
t=time.time(); perf.count_pairs(big,500); assert time.time()-t<2
random.seed(3); items=[random.randint(0,5000) for _ in range(200000)]
t=time.time(); perf.dedupe_keep_order(items); assert time.time()-t<2
print("ALL OK")
