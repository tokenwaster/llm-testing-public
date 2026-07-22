import perf
# [1,2,3,4,3] target 6: pairs i<j with sum 6
# (1,3): 2+4=6, (2,4): 3+3=6 => 2 pairs
print(perf.count_pairs([1,2,3,4,3], 6))
print(perf.count_pairs([1,1,1], 2))
