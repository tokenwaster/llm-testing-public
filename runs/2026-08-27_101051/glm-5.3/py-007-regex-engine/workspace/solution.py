"""A tiny regular-expression engine (no `re` module).

Supported pattern syntax:
    c           literal character (matches itself)
    .           any single character
    X*          zero or more of the preceding element X
    X+          one or more of the preceding element X
    X?          zero or one of the preceding element X
    [abc]       character class
    [a-z0-9]    character class with ranges
    [^abc]      negated character class
    (X may be a literal, '.', or a character class; quantifiers may
     follow classes as well)

`match(pattern, text)` reports whether the pattern matches the ENTIRE
text.  Malformed patterns raise ValueError.  The matcher is a recursive
backtracking engine (with memoization of (token, position) states so
pathological patterns do not blow up exponentially).
"""

import sys

_QUANTIFIERS = "*+?"


def _literal(ch):
    """Matcher for a single literal character."""
    def fn(c):
        return c == ch
    return fn


def _any_char(_c):
    """Matcher for '.' -- any single character."""
    return True


def _parse_class(pattern, start):
    """Parse the character class beginning at pattern[start] == '['.

    Returns (matcher, index_just_past_closing_bracket).
    Raises ValueError for unclosed classes or bad ranges.
    """
    n = len(pattern)
    i = start + 1

    negate = False
    if i < n and pattern[i] == "^":
        negate = True
        i += 1

    ranges = []          # list of (lo, hi) inclusive character ranges
    first = True         # a ']' as the very first member is a literal
    while True:
        if i >= n:
            raise ValueError("unterminated character class")
        ch = pattern[i]
        if ch == "]" and not first:
            i += 1
            break
        first = False

        # A range "X-Y" only when '-' follows X and the character after
        # the '-' exists and is not the closing bracket.
        if i + 2 < n and pattern[i + 1] == "-" and pattern[i + 2] != "]":
            lo, hi = ch, pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError(
                    "invalid character range '%s-%s'" % (lo, hi))
            ranges.append((lo, hi))
            i += 3
        else:
            ranges.append((ch, ch))
            i += 1

    def fn(c):
        inside = any(lo <= c <= hi for lo, hi in ranges)
        return inside != negate

    return fn, i


def _parse(pattern):
    """Compile `pattern` into a list of (matcher, min, max) tokens.

    `max` is None for unbounded repetition.
    Raises ValueError on malformed patterns.
    """
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch in _QUANTIFIERS:
            raise ValueError(
                "quantifier '%s' has nothing to repeat" % ch)

        if ch == "[":
            fn, i = _parse_class(pattern, i)
        else:
            fn = _any_char if ch == "." else _literal(ch)
            i += 1

        lo, hi = 1, 1
        if i < n and pattern[i] in _QUANTIFIERS:
            q = pattern[i]
            if q == "*":
                lo, hi = 0, None
            elif q == "+":
                lo, hi = 1, None
            else:  # '?'
                lo, hi = 0, 1
            i += 1

        tokens.append((fn, lo, hi))
    return tokens


def match(pattern: str, text: str) -> bool:
    """Return True iff `pattern` matches the ENTIRE `text`."""
    tokens = _parse(pattern)

    # Make sure the recursive matcher has room on the stack.
    needed = len(tokens) + 500
    if sys.getrecursionlimit() < needed:
        sys.setrecursionlimit(needed)

    n = len(text)
    memo = {}

    def solve(ti, si):
        """Can tokens[ti:] match text[si:] exactly?"""
        key = (ti, si)
        if key in memo:
            return memo[key]

        if ti == len(tokens):
            result = si == n
        else:
            fn, lo, hi = tokens[ti]

            # Longest run of characters this token can consume at si.
            count = 0
            pos = si
            while (hi is None or count < hi) and pos < n and fn(text[pos]):
                pos += 1
                count += 1

            result = False
            if count >= lo:
                # Greedy: try the longest repetition first, then back off.
                for used in range(count, lo - 1, -1):
                    if solve(ti + 1, si + used):
                        result = True
                        break

        memo[key] = result
        return result

    return solve(0, 0)
