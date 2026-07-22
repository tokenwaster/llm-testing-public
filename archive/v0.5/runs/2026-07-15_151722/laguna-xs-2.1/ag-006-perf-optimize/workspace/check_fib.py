from perf import fib

result = fib(300)
print(f"fib(300) = {result}")
print(f"Type: {type(result)}")

# Let's also check a few smaller values
for n in [0, 1, 2, 3, 10, 20]:
    print(f"fib({n}) = {fib(n)}")