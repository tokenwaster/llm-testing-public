"""A tiny regex engine supporting a small subset of regular expressions.

Supported syntax:
    literal characters      match themselves
    .                       any single character
    *                       zero or more of the preceding element
    +                       one or more of the preceding element
    ?                       zero or one of the preceding element
    [abc] [a-z0-9] [^abc]   character classes, with ranges and negation

`match(pattern, text)` is anchored: the pattern must consume the entire text.
Malformed patterns raise ValueError.
"""

from typing import List, Optional, Set, Tuple

__all__ = ["match", "ValueError"]

# Token element kinds
_ANY = "any"        # '.'
_LITERAL = "lit"    # a single ordinary character
_CLASS = "cls"      # a character class

_QUANTIFIERS = "*+?"


class _Token:
    """One pattern element plus its optional quantifier."""

    __slots__ = ("kind", "char", "negated", "chars", "ranges", "quant")

    def __init__(
        self,
        kind: str,
        char: str = "",
        negated: bool = False,
        chars: Optional[Set[str]] = None,
        ranges: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self.kind = kind
        self.char = char
        self.negated = negated
        self.chars = chars if chars is not None else set()
        self.ranges = ranges if ranges is not None else []
        self.quant = ""  # '', '*', '+' or '?'

    def matches(self, c: str) -> bool:
        if self.kind == _ANY:
            return True
        if self.kind == _LITERAL:
            return c == self.char
        # character class
        inside = c in self.chars or any(lo <= c <= hi for lo, hi in self.ranges)
        return inside != self.negated

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<_Token {self.kind} {self.char!r}{self.quant}>"


def _parse_class(pattern: str, i: int) -> Tuple[_Token, int]:
    """Parse a character class starting at pattern[i] == '['.

    Returns the token and the index just past the closing ']'.
    """
    i += 1  # skip '['
    negated = False
    if i < len(pattern) and pattern[i] == "^":
        negated = True
        i += 1

    chars: Set[str] = set()
    ranges: List[Tuple[str, str]] = []

    # A ']' in the first position is treated as a literal, as in POSIX.
    first = True
    closed = False
    while i < len(pattern):
        c = pattern[i]
        if c == "]" and not first:
            i += 1
            closed = True
            break
        first = False
        # Possible range: X-Y where Y is not the closing bracket.
        if (
            i + 2 < len(pattern)
            and pattern[i + 1] == "-"
            and pattern[i + 2] != "]"
        ):
            lo, hi = c, pattern[i + 2]
            if lo > hi:
                raise ValueError(
                    f"invalid range {lo!r}-{hi!r} in character class"
                )
            ranges.append((lo, hi))
            i += 3
        else:
            chars.add(c)
            i += 1

    if not closed:
        raise ValueError("unterminated character class: missing ']'")
    if not chars and not ranges:
        raise ValueError("empty character class")

    return _Token(_CLASS, negated=negated, chars=chars, ranges=ranges), i


def _parse(pattern: str) -> List[_Token]:
    """Turn a pattern string into a flat list of quantified tokens."""
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a str")

    tokens: List[_Token] = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in _QUANTIFIERS:
            raise ValueError(
                f"quantifier {c!r} at position {i} has nothing to repeat"
            )
        if c == "]":
            raise ValueError(f"unmatched ']' at position {i}")
        if c == "[":
            token, i = _parse_class(pattern, i)
        elif c == ".":
            token = _Token(_ANY)
            i += 1
        else:
            token = _Token(_LITERAL, char=c)
            i += 1

        # Attach at most one quantifier.
        if i < n and pattern[i] in _QUANTIFIERS:
            token.quant = pattern[i]
            i += 1
            if i < n and pattern[i] in _QUANTIFIERS:
                raise ValueError(
                    f"multiple repeat at position {i}"
                )
        tokens.append(token)
    return tokens


def match(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the whole of `text`."""
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    tokens = _parse(pattern)
    if not tokens:
        return text == ""

    ntok = len(tokens)
    ntxt = len(text)
    # (token index, text index) pairs already known to fail.
    failed: Set[Tuple[int, int]] = set()

    def here(ti: int, si: int) -> bool:
        if ti == ntok:
            return si == ntxt
        key = (ti, si)
        if key in failed:
            return False

        tok = tokens[ti]
        quant = tok.quant
        result = False

        if quant == "":
            result = si < ntxt and tok.matches(text[si]) and here(ti + 1, si + 1)
        elif quant == "?":
            result = here(ti + 1, si) or (
                si < ntxt and tok.matches(text[si]) and here(ti + 1, si + 1)
            )
        else:  # '*' or '+' — greedy with backtracking
            lo = 1 if quant == "+" else 0
            # How far can this element stretch?
            end = si
            while end < ntxt and tok.matches(text[end]):
                end += 1
            count = end - si
            if count >= lo:
                for take in range(count, lo - 1, -1):
                    if here(ti + 1, si + take):
                        result = True
                        break

        if not result:
            failed.add(key)
        return result

    return here(0, 0)


if __name__ == "__main__":  # pragma: no cover
    assert match("", "")
    assert not match("", "a")
    assert match("abc", "abc")
    assert not match("abc", "abcd")
    assert match("a.c", "abc")
    assert match("a*b", "aaab")
    assert match("a*b", "b")
    assert not match("a+b", "b")
    assert match("a?b", "b")
    assert match("[a-z]+[0-9]*", "hello42")
    assert not match("[^abc]", "a")
    assert match(".*", "anything at all")
    for bad in ("*a", "[abc", "a**", "+", "]"):
        try:
            match(bad, "x")
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad!r}")
    print("ok")
