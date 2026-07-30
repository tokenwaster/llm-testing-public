

def chunk(items, n):
    if n <= 0:
        raise ValueError("n must be positive")
    return [items[i:i + n] for i in range(0, len(items), n)]


def flatten(items):
    out = []
    for x in items:
        if isinstance(x, (list, tuple)):
            out.extend(x)
        else:
            out.append(x)
    return out


def group_by(items, key):
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


def take_while(items, pred):
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out

# Preserve order while removing duplicates

def unique(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# Return (matches, non-matches) as per tests

def partition(items, pred):
    matches, non_matches = [], []
    for x in items:
        (matches if pred(x) else non_matches).append(x)
    return matches, non_matches

# Include the final window; k must be positive

def windows(items, k):
    if k <= 0:
        raise ValueError("k must be positive")
    return [items[i:i + k] for i in range(0, len(items) - k + 1)]
