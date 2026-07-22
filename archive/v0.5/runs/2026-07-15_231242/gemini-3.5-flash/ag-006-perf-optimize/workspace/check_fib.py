# Let's verify the correct fib(300) value using standard recursion/memoization or simple loop.
# The previous assertion value in test_perf.py might have been slightly off or copy-pasted incorrectly.
# Let's write a quick script to print fib(300) and check.
def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print(fib(300))
