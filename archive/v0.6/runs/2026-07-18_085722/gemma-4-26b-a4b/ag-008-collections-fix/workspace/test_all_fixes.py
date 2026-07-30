def unique(items):
    """Order-preserving de-duplication (first occurrence wins)."""
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result

def partition(items, pred):
    """(matches, non_matches) — items where pred is enough come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return yes, no

def windows(items, k):
    """All contiguous windows of length k, in order."""
    if k <= 0:
        raise ValueError("k must be positive")
    return [items[i:i + k] for i in range(0, len(items) - k + 1)]

# Test the fixes
print(f"Test unique_order: {unique([3, 1, 3, 2, 1]) == [3, 1, 2]}")
print(f"Test partition_orientation: {partition([1, 2, 3, 4], lambda x: x > 2) == ([3, 4], [1, 2])}")
print(f"Test windows_complete: {windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]}")
