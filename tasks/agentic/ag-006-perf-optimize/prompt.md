The workspace contains `perf.py` — a module whose functions are CORRECT but
too slow for production. Your job: make every function fast enough to pass
the timing budgets below while keeping the results identical.

Functions and their required behavior (unchanged):

- `common_elements(a, b)` — sorted list of values appearing in both lists
- `fib(n)` — nth Fibonacci number (fib(0)=0, fib(1)=1)
- `count_pairs(nums, target)` — number of index pairs i<j with
  nums[i]+nums[j] == target
- `dedupe_keep_order(items)` — remove duplicates, preserving first-seen order

Timing budgets (generous — any reasonable algorithmic fix sails through):
- `common_elements` on two 200,000-element lists: under 2 seconds
- `fib(300)`: under 2 seconds
- `count_pairs` on 100,000 elements: under 2 seconds
- `dedupe_keep_order` on 200,000 items: under 2 seconds

Rules: keep the function names and signatures; standard library only; the
module must still import cleanly. Correctness is tested with exact expected
values — optimize the algorithms, don't approximate.
