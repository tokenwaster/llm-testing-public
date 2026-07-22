from perf import *
assert common_elements([3,1,2,2],[2,3,4]) == [2,3]
assert fib(0)==0 and fib(1)==1 and fib(10)==55 and fib(300)==222232244629420445529739893461909967206666939096499764990979600
assert count_pairs([1,1,1,1],2)==6
assert count_pairs([1,2,3,4],5)==2
assert dedupe_keep_order([3,1,3,2,1]) == [3,1,2]
print('ok')
