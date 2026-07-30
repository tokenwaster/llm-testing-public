import random, time
import perf

# test common_elements
n=200000
a=list(range(n))
b=list(range(n//2, n*3//2))
start=time.time()
res=perf.common_elements(a,b)
print('common_elements length', len(res), 'time', time.time()-start)

# test fib
start=time.time()
print('fib300', perf.fib(300))
print('fib time', time.time()-start)

# test count_pairs
nums=[random.randint(0,1000) for _ in range(100000)]
# choose target that likely has some pairs
target=500
start=time.time()
cnt=perf.count_pairs(nums,target)
print('count_pairs result', cnt, 'time', time.time()-start)

# test dedupe_keep_order
items=[random.randint(0,100000) for _ in range(200000)]
start=time.time()
out=perf.dedupe_keep_order(items)
print('dedupe length', len(out), 'time', time.time()-start)
