def mean(values):
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / len(values)


def median(values):
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    # Fixed: average the two middle elements for even-length lists
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    else:
        return s[mid]

def mode_of(values):
    """Most common value; ties broken by first appearance."""
    if not values:
        raise ValueError("mode of empty sequence")
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    best = max(counts.values())
    for v in values:
        if counts[v] == best:
            return v