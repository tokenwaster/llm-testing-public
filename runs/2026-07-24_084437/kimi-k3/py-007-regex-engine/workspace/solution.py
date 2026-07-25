"""A tiny regular-expression matcher built from scratch.

Supports literals, '.', '*', '+', '?', and character classes such as
[abc], [a-z0-9], and [^abc].  The pattern must match the ENTIRE text.
Implemented with recursive backtracking (memoized); the `re` module is
not used.
"""

from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """Return True iff `pattern` matches the whole of `text`."""
    tokens = tuple(_parse(pattern))
    n = len(text)

    @lru_cache(maxsize=None)
    def dp(ti: int, si: int) -> bool:
        """Can tokens[ti:] match text[si:] entirely?"""
        if ti == len(tokens):
            return si == n

        kind, data, quant = tokens[ti]

        if quant is None:  # exactly one occurrence
            return (
                si < n
                and _matches(kind, data, text[si])
                and dp(ti + 1, si + 1)
            )

        if quant == "?":  # zero or one occurrence
            if si < n and _matches(kind, data, text[si]) and dp(ti + 1, si + 1):
                return True
            return dp(ti + 1, si)

        # '*' (zero or more) or '+' (one or more): consume greedily,
        # then backtrack from the longest run down to the minimum.
        end = si
        while end < n and _matches(kind, data, text[end]):
            end += 1
        minimum = 1 if quant == "+" else 0
        for count in range(end - si, minimum - 1, -1):
            if dp(ti + 1, si + count):
                return True
        return False

    return dp(0, 0)


def _matches(kind, data, ch) -> bool:
    """Does a single character satisfy one pattern element?"""
    if kind == "any":
        return True
    if kind == "lit":
        return ch == data
    negate, chars = data  # character class
    return (ch in chars) != negate


def _parse(pattern: str):
    """Turn the pattern into a list of (kind, data, quantifier) tokens."""
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in "*+?":
            raise ValueError("quantifier %r with no preceding element" % c)
        if c == "[":
            kind, data, i = _parse_class(pattern, i)
        elif c == ".":
            kind, data = "any", None
            i += 1
        else:
            kind, data = "lit", c
            i += 1
        quant = None
        if i < n and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1
        tokens.append((kind, data, quant))
    return tokens


def _parse_class(pattern: str, start: int):
    """Parse a character class starting at pattern[start] == '['.

    Returns (kind, data, index_just_after_closing_bracket).
    """
    n = len(pattern)
    i = start + 1
    negate = False
    if i < n and pattern[i] == "^":
        negate = True
        i += 1

    chars = set()
    first = True
    while True:
        if i >= n:
            raise ValueError("unterminated character class: missing ']'")
        c = pattern[i]
        if c == "]":
            if first:
                raise ValueError("empty character class")
            return "class", (negate, frozenset(chars)), i + 1
        # A range like a-z requires: char, '-', char, with the final
        # char not being the closing bracket.
        if i + 2 < n and pattern[i + 1] == "-" and pattern[i + 2] != "]":
            lo, hi = c, pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError("invalid character range %r-%r" % (lo, hi))
            chars.update(chr(code) for code in range(ord(lo), ord(hi) + 1))
            i += 3
        else:
            chars.add(c)
            i += 1
        first = False
