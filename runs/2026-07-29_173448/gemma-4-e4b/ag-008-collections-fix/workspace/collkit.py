

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
    # Note: dictionary keys maintain insertion order from Python 3.7+
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


def unique(items):
    # Order-preserving de-duplication fix
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
        # Fixed logic bug and ensured correct grouping order
        if pred(x):
            yes.append(x)
        else:
            no.append(x)
    # Fix return order based on test_partition_orientation (y=yes, n=no expected)
    return yes, no


def windows(items, k):
    if k <= 0:
        raise ValueError("k must be positive")
    # Fixed range to include the last possible window starting at index L - K
    return [items[i:i + k] for i in range(len(items) - k + 1)]
