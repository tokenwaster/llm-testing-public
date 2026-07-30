def unique(items):
    """Order-preserving de-duplication (first occurrence wins)."""
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result

# Test the fix
print(f"Test 1 (order): {unique([3, 1, 3, 2, 1]) == [3, 1, 2]}")
print(f"Test 2 (empty): {unique([]) == []}")
print(f"Test 3 (all same): {unique([1, 1, 1]) == [1]}")
