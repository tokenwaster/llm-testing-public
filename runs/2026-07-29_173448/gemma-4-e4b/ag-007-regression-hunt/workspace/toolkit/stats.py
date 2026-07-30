def mean(values):
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / len(values)


def median(values):
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    if n % 2 == 0:
        # For even length, the median is the average of the two middle elements.
        return (s[n // 2 - 1] + s[n // 2]) / 2.0
    else:
        # For odd length, the median is the middle element.
        return float(s[n // 2])


def mode_of(values):
    if not values:
        raise ValueError("mode of empty sequence")
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    
    best = 0
    mode_value = None
    max_count = -1

    # Find the maximum frequency
    for count in counts.values():
        if count > max_count:
            max_count = count
            
    # Iterate through values to find all modes (we only need one for now, but let's stick to the test case logic)
    # The current implementation seems to assume returning *a* mode if multiple exist.
    # Since the test relies on "the first encountered" or just any consistent value, 
    # we will return the smallest element that achieves the max_count for consistency/predictability
    # unless specified otherwise by failing tests. The original implementation was simple and returned *a* mode.

    # Let's restore a simplified logic based on the provided test: it seems to want *a* single value.
    max_frequency = 0
    for count in counts.values():
        if count > max_frequency:
            max_frequency = count

    # Find and return the smallest element that has the maximum frequency
    modes = [v for v, count in counts.items() if count == max_frequency]
    return min(modes)
