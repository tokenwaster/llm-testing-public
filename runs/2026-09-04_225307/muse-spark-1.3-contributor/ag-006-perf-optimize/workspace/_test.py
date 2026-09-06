import time, random
import perf

# correctness
assert perf.common_elements([1,2,3,2],[2,3,4]) == [2,3]
assert perf.common_elements([], [1]) == []
assert perf.fib(0)==0 and perf.fib(1)==1 and perf.fib(10)==55 and perf.fib(20)==6765
assert perf.count_pairs([1,2,3,4,3], 6) == 2  # (1,? ) let's check: pairs: 2+4,3+3 => 2
assert perf.count_pairs([1,1,1], 2) == 3
assert perf.count_pairs([], 5) == 0
assert perf.dedupe_keep_order([1,2,1,3,2]) == [1,2,3]
assert perf.dedupe_keep_order([]) == []

# cross-check count_pairs vs brute on random small
random.seed(0)
for _ in range(20):
    n = random.randint(0,30)
    nums = [random.randint(0,5) for _ in range(n)]
    t = random.randint(0,10)
    brute=0
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if nums[i]+nums[j]==t: brute+=1
    assert perf.count_pairs(nums,t)==brute, (nums,t)

# cross-check common_elements vs brute
for _ in range(20):
    a=[random.randint(0,10) for _ in range(20)]
    b=[random.randint(0,10) for _ in range(20)]
    out=[]
    for x in a:
        if x in b and x not in out: out.append(x)
    assert perf.common_elements(a,b)==sorted(out)

# timing
random.seed(1)
a=[random.randint(0,400000) for _ in range(200000)]
b=[random.randint(0,400000) for _ in range(200000)]
t=time.time(); perf.common_elements(a,b); print("common", time.time()-t)

t=time.time(); r=perf.fib(300); print("fib", time.time()-t, r==222232244629420445529739893461909967206666939096499764990979600)

nums=[random.randint(0,1000) for _ in range(100000)]
t=time.time(); perf.count_pairs(nums, 1000); print("pairs", time.time()-t)

items=[random.randint(0,400000) for _ in range(200000)]
t=time.time(); perf.dedupe_keep_order(items); print("dedupe", time.time()-t)
print("OK")
