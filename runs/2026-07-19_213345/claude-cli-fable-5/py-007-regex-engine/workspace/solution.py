"""A small regex matcher supporting literals, '.', '*', '+', '?', and
character classes ([abc], [a-z0-9], [^abc]). Matches the ENTIRE text."""

import sys


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.

    Returns (element, next_index) where element is
    ('class', frozenset_of_chars, negated).
    Raises ValueError on an unclosed class.
    """
    j = i + 1
    negated = False
    if j < len(pattern) and pattern[j] == '^':
        negated = True
        j += 1

    chars = set()
    first = True
    while True:
        if j >= len(pattern):
            raise ValueError(f"unclosed '[' at position {i}")
        c = pattern[j]
        if c == ']' and not first:
            j += 1
            break
        first = False
        # Range like a-z: '-' between two chars, and the char after '-'
        # is not the closing ']'
        if (j + 2 < len(pattern) and pattern[j + 1] == '-'
                and pattern[j + 2] != ']'):
            lo, hi = c, pattern[j + 2]
            if ord(lo) > ord(hi):
                raise ValueError(f"invalid range {lo}-{hi} in class")
            for code in range(ord(lo), ord(hi) + 1):
                chars.add(chr(code))
            j += 3
        else:
            chars.add(c)
            j += 1

    return ('class', frozenset(chars), negated), j


def _parse(pattern):
    """Parse pattern into a list of (element, quantifier) pairs.

    element is ('char', c), ('dot',), or ('class', frozenset, negated).
    quantifier is one of None, '*', '?' ('+' is expanded to elem + elem*).
    """
    elems = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c in '*+?':
            raise ValueError(
                f"quantifier {c!r} at position {i} has no preceding element")
        if c == '[':
            elem, i = _parse_class(pattern, i)
        elif c == '.':
            elem = ('dot',)
            i += 1
        else:
            elem = ('char', c)
            i += 1

        quant = None
        if i < len(pattern) and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            # Reject stacked quantifiers like a** or a+?
            if i < len(pattern) and pattern[i] in '*+?':
                raise ValueError(
                    f"quantifier {pattern[i]!r} at position {i} "
                    f"has no preceding element")

        if quant == '+':
            elems.append((elem, None))
            elems.append((elem, '*'))
        else:
            elems.append((elem, quant))
    return elems


def _matches_char(elem, ch):
    kind = elem[0]
    if kind == 'char':
        return ch == elem[1]
    if kind == 'dot':
        return True
    # class
    _, chars, negated = elem
    return (ch not in chars) if negated else (ch in chars)


def match(pattern: str, text: str) -> bool:
    elems = _parse(pattern)

    def m(ei, ti):
        if ei == len(elems):
            return ti == len(text)
        elem, quant = elems[ei]
        if quant is None:
            return (ti < len(text) and _matches_char(elem, text[ti])
                    and m(ei + 1, ti + 1))
        if quant == '?':
            if (ti < len(text) and _matches_char(elem, text[ti])
                    and m(ei + 1, ti + 1)):
                return True
            return m(ei + 1, ti)
        # '*': greedy with backtracking
        k = ti
        while k < len(text) and _matches_char(elem, text[k]):
            k += 1
        while k >= ti:
            if m(ei + 1, k):
                return True
            k -= 1
        return False

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 10 * (len(elems) + len(text)) + 1000))
    try:
        return m(0, 0)
    finally:
        sys.setrecursionlimit(old_limit)
