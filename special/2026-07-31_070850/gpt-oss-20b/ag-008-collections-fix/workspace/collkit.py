

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
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def partition(items, pred):
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    # Return matches first as expected by tests
    return yes, no


def windows(items, k):
    if k <= 0:
        raise ValueError("k must be positive")
    # Include the final window when len - k + 1 > 0
    return [items[i:i + k] for i in range(0, len(items) - k + 1)]
