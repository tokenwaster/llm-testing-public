import perf

print("Module imported successfully")
print("Functions available:")
print(f"  - common_elements: {callable(perf.common_elements)}")
print(f"  - fib: {callable(perf.fib)}")
print(f"  - count_pairs: {callable(perf.count_pairs)}")
print(f"  - dedupe_keep_order: {callable(perf.dedupe_keep_order)}")
