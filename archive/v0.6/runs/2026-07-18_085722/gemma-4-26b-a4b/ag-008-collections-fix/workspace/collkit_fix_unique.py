def unique(items):
    """Order-preserving de-duplication (first occurrence wins)."""
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result
