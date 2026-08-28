import random
from collections import Counter
import perf

rng = random.Random(42)
# reproduce the same rng state sequence as the test? just make a fresh one
rng = random.Random(7)
nums = [rng.randrange(0, 1000) for _ in range(100000)]
target = 999

got = perf.count_pairs(nums, target)

cnt = Counter(nums)
exp = sum(v * (cnt.get(target - k, 0) if k != target - k else v - 1)
          for k, v in cnt.items()) // 2

print("perf :", got)
print("counter:", exp)
print("match:", got == exp)

# brute force on a smaller slice with same distribution
small = [rng.randrange(0, 1000) for _ in range(300)]
brute = 0
for i in range(len(small)):
    for j in range(i + 1, len(small)):
        if small[i] + small[j] == 999:
            brute += 1
print("small perf:", perf.count_pairs(small, 999), "small brute:", brute)

# check parity / off-by-one on the big one with a third method
seen = {}
total = 0
for x in nums:
    total += seen.get(target - x, 0)
    seen[x] = seen.get(x, 0) + 1
print("streaming:", total)
