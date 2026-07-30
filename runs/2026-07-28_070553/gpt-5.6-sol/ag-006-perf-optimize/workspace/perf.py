def common_elements(a, b):
    """Return the distinct values shared by *a* and *b*, in sorted order."""
    try:
        common = set(a).intersection(b)
    except TypeError:
        # Retain the original behavior for collections containing unhashable
        # values.  The fast path above covers the normal (and large) case.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)
    return sorted(common)


def fib(n):
    """Return the nth Fibonacci number."""
    if n < 2:
        return n

    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def count_pairs(nums, target):
    """Count index pairs whose values add up to target."""
    seen = {}
    count = 0
    try:
        for value in nums:
            count += seen.get(target - value, 0)
            seen[value] = seen.get(value, 0) + 1
        return count
    except TypeError:
        # Preserve support for unusual, non-hashable/addition-only values.
        count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    count += 1
        return count


def dedupe_keep_order(items):
    """Remove duplicates while retaining their first-seen order."""
    out = []
    seen = set()
    use_set = True

    for value in items:
        if use_set:
            try:
                if value in seen:
                    continue
                seen.add(value)
                out.append(value)
                continue
            except TypeError:
                # Once an unhashable value appears, list membership is needed
                # to preserve equality semantics across all prior values too.
                use_set = False

        if value not in out:
            out.append(value)

    return out
