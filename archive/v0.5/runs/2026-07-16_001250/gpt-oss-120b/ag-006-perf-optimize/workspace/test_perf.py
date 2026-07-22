import random, time, perf

# test common_elements
n=200000
a = list(range(n))
b = list(range(n//2, n + n//2))
start=time.time()
res=perf.common_elements(a,b)
print('common_elements len',len(res), 'time', time.time()-start)

# test fib
start=time.time()
print('fib300', perf.fib(300))
print('fib time', time.time()-start)

# test count_pairs
nums = [random.randint(0,1000) for _ in range(100000)]
target = 500
start=time.time()
cnt=perf.count_pairs(nums,target)
print('count_pairs result', cnt, 'time', time.time()-start)

# test dedupe_keep_order
items = list(range(100000)) + list(range(50000))
start=time.time()
out=perf.dedupe_keep_order(items)
print('dedupe len', len(out), 'time', time.time()-start)
