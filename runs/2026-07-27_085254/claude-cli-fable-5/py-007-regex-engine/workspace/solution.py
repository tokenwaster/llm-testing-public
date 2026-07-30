"""A small regex engine supporting ., *, +, ?, and character classes.

match(pattern, text) reports whether the pattern matches the entire text.
Implemented as a recursive backtracking matcher over a parsed element list.
"""


def _parse(pattern):
    """Parse pattern into a list of (matcher, quantifier) elements.

    matcher is a predicate over a single character; quantifier is one of
    '' (exactly one), '*', '+', '?'. Raises ValueError on malformed input.
    """
    elements = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in "*+?":
            raise ValueError(
                f"quantifier {c!r} at position {i} has no preceding element"
            )
        if c == "[":
            matcher, i = _parse_class(pattern, i)
        elif c == ".":
            matcher = lambda ch: True
            i += 1
        else:
            matcher = (lambda lit: lambda ch: ch == lit)(c)
            i += 1
        quant = ""
        if i < n and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1
        elements.append((matcher, quant))
    return elements


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.

    Returns (matcher, index_after_closing_bracket).
    """
    n = len(pattern)
    i += 1  # skip '['
    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1

    singles = set()
    ranges = []
    first = True
    while True:
        if i >= n:
            raise ValueError("unclosed character class '['")
        c = pattern[i]
        if c == "]" and not first:
            i += 1
            break
        first = False
        # A '-' with a character on both sides (and ']' not next) is a range.
        if i + 2 < n and pattern[i + 1] == "-" and pattern[i + 2] != "]":
            lo, hi = c, pattern[i + 2]
            if lo > hi:
                raise ValueError(f"invalid range {lo}-{hi} in character class")
            ranges.append((lo, hi))
            i += 3
        else:
            singles.add(c)
            i += 1

    def matcher(ch):
        inside = ch in singles or any(lo <= ch <= hi for lo, hi in ranges)
        return inside != negated

    return matcher, i


def _match_here(elements, ei, text, ti):
    """Backtracking match of elements[ei:] against text[ti:]."""
    if ei == len(elements):
        return ti == len(text)
    matcher, quant = elements[ei]

    if quant == "":
        return (
            ti < len(text)
            and matcher(text[ti])
            and _match_here(elements, ei + 1, text, ti + 1)
        )
    if quant == "?":
        if ti < len(text) and matcher(text[ti]):
            if _match_here(elements, ei + 1, text, ti + 1):
                return True
        return _match_here(elements, ei + 1, text, ti)
    if quant == "+":
        if not (ti < len(text) and matcher(text[ti])):
            return False
        ti += 1
        # fall through to star-like behavior for the remaining repetitions
    # '*' (and the tail of '+'): try longest first, backtrack toward zero.
    end = ti
    while end < len(text) and matcher(text[end]):
        end += 1
    for stop in range(end, ti - 1, -1):
        if _match_here(elements, ei + 1, text, stop):
            return True
    return False


def match(pattern: str, text: str) -> bool:
    elements = _parse(pattern)
    return _match_here(elements, 0, text, 0)
