"""A tiny regular-expression matcher for a restricted syntax, built from
scratch (no `re` module). Matching is done by recursive backtracking over
the parsed pattern elements, memoized to avoid exponential blow-ups."""

import sys
from functools import lru_cache

_QUANTIFIERS = frozenset("*+?")


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.

    Supports literal members, ranges like a-z, negation via a leading ^,
    a literal ] in first position, and a literal - at either end.
    Returns (chars, negated, next_index).
    """
    i += 1  # consume '['
    negated = False
    if i < len(pattern) and pattern[i] == "^":
        negated = True
        i += 1

    chars = set()
    first = True
    while True:
        if i >= len(pattern):
            raise ValueError("unterminated character class")
        c = pattern[i]
        if c == "]" and not first:
            return chars, negated, i + 1
        first = False
        # A range like a-z (a '-' at the very end of the class is a literal).
        if (
            i + 2 < len(pattern)
            and pattern[i + 1] == "-"
            and pattern[i + 2] != "]"
        ):
            lo, hi = c, pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError("bad character range %r-%r" % (lo, hi))
            chars.update(chr(code) for code in range(ord(lo), ord(hi) + 1))
            i += 3
        else:
            chars.add(c)
            i += 1


def _parse(pattern):
    """Parse the pattern into a list of (predicate, quantifier) elements.

    quantifier is one of None (exactly one), '*', '+' or '?'.
    """
    elements = []
    i, n = 0, len(pattern)
    while i < n:
        ch = pattern[i]
        if ch in _QUANTIFIERS:
            raise ValueError("quantifier %r has no preceding element" % ch)
        if ch == "[":
            chars, negated, i = _parse_class(pattern, i)
            if negated:
                pred = lambda c, s=chars: c not in s
            else:
                pred = lambda c, s=chars: c in s
        elif ch == ".":
            pred = lambda c: True
            i += 1
        else:
            pred = lambda c, lit=ch: c == lit
            i += 1
        quant = None
        if i < n and pattern[i] in _QUANTIFIERS:
            quant = pattern[i]
            i += 1
        elements.append((pred, quant))
    return elements


def match(pattern: str, text: str) -> bool:
    """Report whether `pattern` matches the ENTIRE `text`."""
    elements = _parse(pattern)

    # Recursion depth is bounded by the number of pattern elements.
    if len(elements) + 100 > sys.getrecursionlimit():
        sys.setrecursionlimit(len(elements) + 1000)

    @lru_cache(maxsize=None)
    def solve(pi, ti):
        """Can elements[pi:] match text[ti:] entirely?"""
        if pi == len(elements):
            return ti == len(text)
        pred, quant = elements[pi]
        if quant is None:
            return ti < len(text) and pred(text[ti]) and solve(pi + 1, ti + 1)
        if quant == "?":
            if ti < len(text) and pred(text[ti]) and solve(pi + 1, ti + 1):
                return True
            return solve(pi + 1, ti)
        # '*' or '+': consume as many characters as possible (greedy),
        # then backtrack one at a time until the rest of the pattern matches.
        end = ti
        while end < len(text) and pred(text[end]):
            end += 1
        first_allowed = ti if quant == "*" else ti + 1
        for k in range(end, first_allowed - 1, -1):
            if solve(pi + 1, k):
                return True
        return False

    return solve(0, 0)
