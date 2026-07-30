"""collkit — small collection utilities. Some functions have bugs; the test
suite in tests/ shows which. Fix the bugs in THIS file so every test passes."""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter)."""
    if n <= 0:
        raise ValueError("n must be positive")
    return [items[i:i + n] for i in range(0, len(items), n)]


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""
    out = []
    for x in items:
        if isinstance(x, (list, tuple)):
            out.extend(x)
        else:
            out.append(x)
    return out


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


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
    """(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return yes, no


def windows(items, k):
    """All contiguous windows of length k, in order."""
    if k <= 0:
        raise ValueError("k must be positive")
    return [items[i:i + k] for i in range(0, len(items) - k + 1)]
