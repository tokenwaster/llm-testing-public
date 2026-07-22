def mean(values):
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / len(values)


def median(values):
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    # If n is odd, the middle element is at index n // 2.
    # If n is even, we average the two middle elements: s[n//2 - 1] and s[n//2].
    if n % 2 == 1:
        return s[n // 2]
    else:
        mid1 = s[n // 2 - 1]
        mid2 = s[n // 2]
        return (mid1 + mid2) / 2