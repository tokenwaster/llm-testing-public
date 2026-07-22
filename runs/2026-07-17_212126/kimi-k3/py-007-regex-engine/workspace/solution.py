"""Hand-rolled regular-expression matcher for a small regex subset.

Supported syntax:
    - literal characters (match themselves)
    - '.'   any single character
    - '*'   zero or more of the preceding element
    - '+'   one or more of the preceding element
    - '?'   zero or one of the preceding element
    - character classes: [abc], ranges like [a-z0-9], negation [^abc]
      (a quantifier may follow a class)

The match must cover the ENTIRE text.  Malformed patterns raise ValueError.
"""

import sys
from functools import lru_cache

__all__ = ["match"]

_QUANTIFIERS = frozenset("*+?")


def _parse_class(pattern, start):
    """Parse a character class beginning at pattern[start] == '['.

    Returns (predicate, next_index) where predicate(ch) -> bool.
    """
    n = len(pattern)
    j = start + 1
    negate = False
    if j < n and pattern[j] == "^":
        negate = True
        j += 1

    chars = set()
    while j < n and pattern[j] != "]":
        # A range x-y, but a '-' right before ']' is a literal '-'.
        if j + 2 < n and pattern[j + 1] == "-" and pattern[j + 2] != "]":
            lo, hi = pattern[j], pattern[j + 2]
            if ord(lo) > ord(hi):
                raise ValueError(
                    "invalid range %r-%r in character class" % (lo, hi)
                )
            chars.update(chr(c) for c in range(ord(lo), ord(hi) + 1))
            j += 3
        else:
            chars.add(pattern[j])
            j += 1

    if j >= n:
        raise ValueError("unclosed character class")
    if not chars:
        raise ValueError("empty character class")
    j += 1  # consume ']'

    frozen = frozenset(chars)
    if negate:
        return (lambda ch, s=frozen: ch not in s), j
    return (lambda ch, s=frozen: ch in s), j


def _parse(pattern):
    """Turn a pattern string into a list of (predicate, quantifier) tokens."""
    n = len(pattern)
    tokens = []
    i = 0
    while i < n:
        c = pattern[i]
        if c in _QUANTIFIERS:
            raise ValueError("quantifier %r has no preceding element" % c)
        if c == "[":
            pred, i = _parse_class(pattern, i)
        elif c == ".":
            pred = lambda ch: True
            i += 1
        else:
            pred = lambda ch, lit=c: ch == lit
            i += 1

        quant = None
        if i < n and pattern[i] in _QUANTIFIERS:
            quant = pattern[i]
            i += 1
        tokens.append((pred, quant))
    return tokens


def match(pattern, text):
    """Return True iff the whole of `text` is matched by `pattern`."""
    if not isinstance(pattern, str) or not isinstance(text, str):
        raise TypeError("pattern and text must be strings")

    tokens = _parse(pattern)
    m = len(text)

    # Recursion depth is bounded by the number of tokens; make room if needed.
    needed = 2 * len(tokens) + 100
    if sys.getrecursionlimit() < needed:
        sys.setrecursionlimit(needed)

    @lru_cache(maxsize=None)
    def solve(ti, si):
        """Can tokens[ti:] match text[si:] entirely?"""
        if ti == len(tokens):
            return si == m

        pred, quant = tokens[ti]

        if quant is None:  # exactly one occurrence
            return si < m and pred(text[si]) and solve(ti + 1, si + 1)

        if quant == "?":  # zero or one (greedy: try one first)
            if si < m and pred(text[si]) and solve(ti + 1, si + 1):
                return True
            return solve(ti + 1, si)

        # '*' or '+': find the longest run this element could consume,
        # then backtrack from the longest attempt down to the shortest.
        k = si
        while k < m and pred(text[k]):
            k += 1
        shortest = si + 1 if quant == "+" else si
        if k < shortest:
            return False
        for end in range(k, shortest - 1, -1):
            if solve(ti + 1, end):
                return True
        return False

    return solve(0, 0)
