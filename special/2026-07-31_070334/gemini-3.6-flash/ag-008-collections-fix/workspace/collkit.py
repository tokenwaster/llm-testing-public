"""Collection processing utilities."""

def chunk(seq, size):
    """Split sequence into chunks of given size."""
    return [seq[i:i + size] for i in range(0, len(seq), size)]

def flatten(nested):
    """Flatten a list of lists into a single list."""
    return [item for sublist in nested for item in sublist]

def group_by(seq, key_fn):
    """Group items by the result of key_fn."""
    res = {}
    for item in seq:
        k = key_fn(item)
        res.setdefault(k, []).append(item)
    return res

def partition(seq, pred):
    """Partition sequence into (matches, non_matches)."""
    trues, falses = [], []
    for item in seq:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses

def take_while(seq, pred):
    """Take items from seq while pred holds."""
    res = []
    for item in seq:
        if not pred(item):
            break
        res.append(item)
    return res

def unique(seq):
    """Return sequence items with duplicates removed."""
    seen = set()
    res = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            res.append(item)
    return res

def windows(seq, size):
    """Return sliding windows of size n over sequence."""
    return [seq[i:i + size] for i in range(len(seq) - size + 1)]
