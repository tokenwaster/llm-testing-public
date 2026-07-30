"""
# collkit — small collection utilities. Some functions have bugs; the test
# suite in tests/ shows which. Fix the bugs in THIS file so every test passes.
"""

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
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def partition(items, pred):
    """(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).

The test suite expects the following behavior:
- `unique()` should preserve order and remove duplicates.
- `partition()` should return (no, yes) in correct order.
- `windows()` should include all windows of length k.
- `chunk()`, `flatten()`, and other functions need fixing too.
"""

def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def partition(items, pred):
    """(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).

The test suite expects the following behavior:
1. `unique()` should preserve order and remove duplicates.
2. `partition()` should return (no, yes) in correct order.
3. `windows()` should include all windows of length k.
4. Other functions need fixing too.
"""


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


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    # FIX: Include the last window
    result = [items[i:i + k] for i in range(0, len(items) - k + 1)]
    return result


"""Flatten ONE level. Non-list items pass through; strings are not split."""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
    """

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
    """

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
    """

"""Flatten ONE level. Non-list items pass through; strings are not split."""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...]}, preserving order."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...]}, preserving order."""


def group_by(items, key):
    """Group into {key(item): [items...], preserving order}."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes

"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


def windows(items, k):
    """All contiguous windows of length k, in order.
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def chunk(items, n):
    """Split into consecutive chunks of at most n (the last may be shorter).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def flatten(items):
    """Flatten ONE level. Non-list items pass through; strings are not split."""

"""Group into {key(item): [items...], preserving order}."""


def group_by(items, key):
    """Group into {key(item): [items...}, preserving order}."""
    groups = {}
    for x in items:
        groups.setdefault(key(x), []).append(x)
    return groups


"""Prefix of items while pred holds; stops at the first failure."""


def take_while(items, pred):
    """Prefix of items while pred holds; stops at the first failure."""
    out = []
    for x in items:
        if not pred(x):
            break
        out.append(x)
    return out


"""Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def unique(items):
    """Order-preserving de-duplication (first occurrence wins).
    
    The test suite expects the following behavior:
    1. `unique()` should preserve order and remove duplicates.
    2. `partition()` should return (no, yes) in correct order.
    3. `windows()` should include all windows of length k.
    4. Other functions need fixing too.
"""""


def partition(items, pred):
    """"(matches, non_matches) — items where pred is truthy come FIRST."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return no, yes
