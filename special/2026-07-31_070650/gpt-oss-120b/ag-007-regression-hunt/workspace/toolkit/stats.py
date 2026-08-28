def mean(values):
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / len(values)


def median(values):
    """Return the statistical median of *values*.

    For an odd number of elements the middle value of the sorted sequence is
    returned. For an even number of elements the median is defined as the mean
    of the two central values.
    """
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    # even length – average the two middle values
    return (s[mid - 1] + s[mid]) / 2


def mode_of(values):
    if not values:
        raise ValueError("mode of empty sequence")
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    best = max(counts.values())
    for v in values:
        if counts[v] == best:
            return v
