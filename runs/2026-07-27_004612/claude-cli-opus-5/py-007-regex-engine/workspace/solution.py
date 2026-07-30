"""A small backtracking regex matcher.

Supported syntax:
  - literal characters
  - ``.``           any single character
  - ``*``           zero or more of the preceding element
  - ``+``           one or more of the preceding element
  - ``?``           zero or one of the preceding element
  - ``[abc]``       character class
  - ``[a-z0-9]``    ranges inside a class
  - ``[^abc]``      negated class

The whole text must be consumed for a match to be reported.
"""

from typing import List, Optional, Tuple


class _Element:
    """A single matchable unit plus its repetition quantifier."""

    __slots__ = ("kind", "chars", "ranges", "negated", "quant")

    def __init__(self, kind: str) -> None:
        self.kind = kind          # "literal", "any" or "class"
        self.chars = ""           # for "literal"
        self.ranges: List[Tuple[str, str]] = []   # for "class"
        self.negated = False      # for "class"
        self.quant = ""           # "", "*", "+" or "?"

    def matches(self, ch: str) -> bool:
        if self.kind == "any":
            return True
        if self.kind == "literal":
            return ch == self.chars
        inside = any(lo <= ch <= hi for lo, hi in self.ranges)
        return inside != self.negated


def _parse_class(pattern: str, i: int) -> Tuple[_Element, int]:
    """Parse a ``[...]`` class starting at ``pattern[i] == '['``.

    Returns the element and the index just past the closing bracket.
    """
    i += 1  # skip '['
    element = _Element("class")
    if i < len(pattern) and pattern[i] == "^":
        element.negated = True
        i += 1

    saw_member = False
    while True:
        if i >= len(pattern):
            raise ValueError("unclosed character class")
        if pattern[i] == "]" and saw_member:
            return element, i + 1
        if pattern[i] == "]" and not saw_member:
            # A ']' immediately after '[' or '[^' is a literal member.
            element.ranges.append(("]", "]"))
            saw_member = True
            i += 1
            continue

        lo = pattern[i]
        i += 1
        # A '-' is a range only when it sits between two members.
        if i + 1 < len(pattern) and pattern[i] == "-" and pattern[i + 1] != "]":
            hi = pattern[i + 1]
            if hi < lo:
                raise ValueError("invalid range in character class")
            element.ranges.append((lo, hi))
            i += 2
        else:
            element.ranges.append((lo, lo))
        saw_member = True


def _parse(pattern: str) -> List[_Element]:
    elements: List[_Element] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch in "*+?":
            raise ValueError("quantifier with nothing to repeat")
        if ch == "]":
            raise ValueError("unmatched ']'")

        if ch == "[":
            element, i = _parse_class(pattern, i)
        elif ch == ".":
            element = _Element("any")
            i += 1
        else:
            element = _Element("literal")
            element.chars = ch
            i += 1

        if i < len(pattern) and pattern[i] in "*+?":
            element.quant = pattern[i]
            i += 1
            if i < len(pattern) and pattern[i] in "*+?":
                raise ValueError("nested quantifier")

        elements.append(element)
    return elements


def _match_here(elements: List[_Element], ei: int, text: str, ti: int) -> bool:
    if ei == len(elements):
        return ti == len(text)

    element = elements[ei]
    quant = element.quant

    if quant == "":
        return (
            ti < len(text)
            and element.matches(text[ti])
            and _match_here(elements, ei + 1, text, ti + 1)
        )

    if quant == "?":
        if _match_here(elements, ei + 1, text, ti):
            return True
        return (
            ti < len(text)
            and element.matches(text[ti])
            and _match_here(elements, ei + 1, text, ti + 1)
        )

    # '*' and '+': consume greedily, then back off one repetition at a time.
    minimum = 1 if quant == "+" else 0
    end = ti
    while end < len(text) and element.matches(text[end]):
        end += 1
    while end - ti >= minimum:
        if _match_here(elements, ei + 1, text, end):
            return True
        end -= 1
    return False


def match(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the entirety of `text`."""
    if not isinstance(pattern, str) or not isinstance(text, str):
        raise TypeError("pattern and text must be strings")
    elements = _parse(pattern)
    if not elements:
        return text == ""
    return _match_here(elements, 0, text, 0)
