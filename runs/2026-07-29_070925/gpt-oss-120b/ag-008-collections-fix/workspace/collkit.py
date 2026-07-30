def chunk(items, n):
    """Split *items* into chunks of size *n*.

    The last chunk may be shorter if the length of *items* is not a multiple of
    *n*. Raises ``ValueError`` for non‑positive *n*.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    return [items[i:i + n] for i in range(0, len(items), n)]


def flatten(items):
    """Flatten a one‑level nested iterable.

    Elements that are ``list`` or ``tuple`` are expanded, other elements are
    left untouched.
    """
    out = []
    for x in items:
        if isinstance(x, (list, tuple)):
            out.extend(x)
        else:
            out.append(x)
    return out


def group_by(items, key):
    """Group *items* by the result of ``key(item)``.

    Returns a dictionary mapping each key to a list of items that produced it.
    """
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


def take_while(items, pred):
    """Return the longest prefix of *items* for which ``pred`` is true.
    """
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def unique(items):
    """Return a list of items preserving original order while removing duplicates.

    This implementation is order‑preserving, unlike ``list(set(items))``.
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def partition(items, pred):
    """Partition *items* into two lists based on *pred*.

    Returns a tuple ``(yes, no)`` where ``yes`` contains the elements for which
    ``pred`` returns ``True`` and ``no`` contains the remaining elements.
    """
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return yes, no


def windows(items, k):
    """Generate sliding windows of length *k* over *items*.

    The windows are overlapping and the final window starts at ``len(items) - k``.
    Raises ``ValueError`` if *k* is not positive.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    return [items[i:i + k] for i in range(0, len(items) - k + 1)]
