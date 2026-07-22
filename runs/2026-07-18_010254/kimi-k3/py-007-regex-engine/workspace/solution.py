"""A tiny regex-subset matcher implemented from scratch (no `re` module).

Supported syntax:
  - literal characters
  - `.`   any single character
  - `*`   zero or more of the preceding element
  - `+`   one or more of the preceding element
  - `?`   zero or one of the preceding element
  - character classes: [abc], ranges [a-z0-9], negation [^abc]
    (a class may be followed by *, +, or ?)

`match` reports whether the pattern matches the ENTIRE text.
Malformed patterns raise ValueError.
"""

import sys
from functools import lru_cache

_QUANTIFIERS = frozenset("*+?")


def _parse_class(pattern, start):
    """Parse a character class starting at pattern[start] == '['.

    Returns (predicate, index just past the closing ']').
    """
    i = start + 1
    n = len(pattern)

    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1

    chars = set()

    # A ']' as the very first character of a class is a literal.
    if i < n and pattern[i] == "]":
        chars.add("]")
        i += 1

    while i < n and pattern[i] != "]":
        # A range x-y, unless the '-' is the last character before ']'.
        if i + 2 < n and pattern[i + 1] == "-" and pattern[i + 2] != "]":
            lo, hi = pattern[i], pattern[i + 2]
            if lo > hi:
                raise ValueError(f"invalid character range {lo!r}-{hi!r}")
            chars.update(chr(code) for code in range(ord(lo), ord(hi) + 1))
            i += 3
        else:
            chars.add(pattern[i])
            i += 1

    if i >= n:
        raise ValueError("unterminated character class '['")
    if not chars:
        raise ValueError("empty character class")
    i += 1  # consume the closing ']'

    frozen = frozenset(chars)
    if negated:
        return (lambda ch, s=frozen: ch not in s), i
    return (lambda ch, s=frozen: ch in s), i


def _parse(pattern):
    """Parse a pattern into a list of (predicate, quantifier) tokens."""
    tokens = []
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c in _QUANTIFIERS:
            raise ValueError(f"quantifier {c!r} has no preceding element")
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


def match(pattern: str, text: str) -> bool:
    """Return True iff `pattern` matches the entire `text`."""
    tokens = _parse(pattern)
    last = len(tokens)
    text_len = len(text)

    # Deep inputs may need more than the default recursion limit.
    needed = text_len + last + 100
    if needed > sys.getrecursionlimit():
        sys.setrecursionlimit(needed + 1000)

    @lru_cache(maxsize=None)
    def search(ti, si):
        """Can tokens[ti:] match text[si:] entirely?"""
        if ti == last:
            return si == text_len
        pred, quant = tokens[ti]

        if quant == "*":
            # Zero occurrences, or consume one char and stay on this token.
            return search(ti + 1, si) or (
                si < text_len and pred(text[si]) and search(ti, si + 1)
            )
        if quant == "+":
            # Consume one char, then either move on or keep consuming.
            return si < text_len and pred(text[si]) and (
                search(ti + 1, si + 1) or search(ti, si + 1)
            )
        if quant == "?":
            # Skip it, or consume exactly one matching char.
            return search(ti + 1, si) or (
                si < text_len and pred(text[si]) and search(ti + 1, si + 1)
            )
        # No quantifier: exactly one matching character.
        return si < text_len and pred(text[si]) and search(ti + 1, si + 1)

    return search(0, 0)
