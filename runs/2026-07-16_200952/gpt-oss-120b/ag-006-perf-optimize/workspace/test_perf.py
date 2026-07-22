import random, time, sys
import perf

def test_common_elements():
    n=200000
    a=list(range(n))
    b=list(range(n//2, n*3//2))
    start=time.time()
    res=perf.common_elements(a,b)
    print('common_elements length',len(res),'time',time.time()-start)

def test_fib():
    start=time.time()
    val=perf.fib(300)
    print('fib300',val,'time',time.time()-start)

def test_count_pairs():
    nums=[random.randint(0,1000) for _ in range(100000)]
    target=500
    start=time.time()
    cnt=perf.count_pairs(nums,target)
    print('count_pairs',cnt,'time',time.time()-start)

def test_dedupe_keep_order():
    items=list(range(100000))+list(range(100000))
    random.shuffle(items)
    start=time.time()
    out=perf.dedupe_keep_order(items)
    print('dedupe length',len(out),'time',time.time()-start)

if __name__=='__main__':
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
