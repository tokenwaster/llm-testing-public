"""A small regex engine supporting literals, '.', '*', '+', '?' and character classes.

Public API:
    match(pattern, text) -> bool   # full match (the whole text must be consumed)
"""

from typing import List, Tuple, Any

__all__ = ["match"]

_QUANTIFIERS = "*+?"


# --------------------------------------------------------------------------- #
# Pattern parsing
# --------------------------------------------------------------------------- #
def _parse_class(pattern: str, i: int) -> Tuple[Tuple[str, bool, List[Any]], int]:
    """Parse a character class starting at pattern[i] == '['.

    Returns ((kind, negated, items), next_index).
    """
    n = len(pattern)
    assert pattern[i] == "["
    i += 1

    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1

    items: List[Any] = []
    items_start = i

    while True:
        if i >= n:
            raise ValueError("unterminated character class: missing ']'")

        ch = pattern[i]

        # A ']' that is the very first character of the class body is a literal.
        if ch == "]" and i != items_start:
            break

        # Possible range: X-Y (but a trailing '-' before ']' is a literal '-')
        if (
            i + 2 < n
            and pattern[i + 1] == "-"
            and pattern[i + 2] != "]"
        ):
            lo, hi = ch, pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError("invalid character range in class: %r-%r" % (lo, hi))
            items.append(("range", lo, hi))
            i += 3
            continue

        items.append(("char", ch))
        i += 1

    # pattern[i] == ']'
    i += 1

    if not items:
        raise ValueError("empty character class")

    return ("class", negated, items), i


def _parse(pattern: str) -> List[Tuple[Tuple, Any]]:
    """Turn a pattern string into a list of (token, quantifier) pairs.

    token is one of:
        ('any',)
        ('lit', ch)
        ('class', negated, items)
    quantifier is None, '*', '+' or '?'.
    """
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a str")

    tokens: List[Tuple[Tuple, Any]] = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch in _QUANTIFIERS:
            raise ValueError("quantifier %r has nothing to repeat" % ch)

        if ch == "]":
            raise ValueError("unmatched ']' in pattern")

        if ch == "[":
            token, i = _parse_class(pattern, i)
        elif ch == ".":
            token = ("any",)
            i += 1
        else:
            token = ("lit", ch)
            i += 1

        quant = None
        if i < n and pattern[i] in _QUANTIFIERS:
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in _QUANTIFIERS:
                raise ValueError(
                    "multiple repeat: %r follows %r" % (pattern[i], quant)
                )

        tokens.append((token, quant))

    return tokens


# --------------------------------------------------------------------------- #
# Matching
# --------------------------------------------------------------------------- #
def _class_matches(negated: bool, items: List[Any], ch: str) -> bool:
    found = False
    for item in items:
        if item[0] == "char":
            if ch == item[1]:
                found = True
                break
        else:  # range
            if item[1] <= ch <= item[2]:
                found = True
                break
    return (not found) if negated else found


def _token_matches(token: Tuple, ch: str) -> bool:
    kind = token[0]
    if kind == "any":
        return True
    if kind == "lit":
        return ch == token[1]
    # class
    return _class_matches(token[1], token[2], ch)


def match(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the entirety of `text`."""
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    tokens = _parse(pattern)
    n_tokens = len(tokens)
    n_text = len(text)
    memo = {}

    def go(ti: int, si: int) -> bool:
        key = (ti, si)
        cached = memo.get(key)
        if cached is not None:
            return cached

        if ti == n_tokens:
            result = si == n_text
            memo[key] = result
            return result

        token, quant = tokens[ti]

        if quant is None:
            result = (
                si < n_text
                and _token_matches(token, text[si])
                and go(ti + 1, si + 1)
            )
            memo[key] = result
            return result

        # How many consecutive characters starting at si does this token match?
        run = 0
        limit = 1 if quant == "?" else n_text - si
        while run < limit and _token_matches(token, text[si + run]):
            run += 1

        low = 1 if quant == "+" else 0

        result = False
        # Greedy: try the longest repetition first.
        for count in range(run, low - 1, -1):
            if go(ti + 1, si + count):
                result = True
                break

        memo[key] = result
        return result

    return go(0, 0)


if __name__ == "__main__":
    tests = [
        ("", "", True),
        ("", "a", False),
        ("abc", "abc", True),
        ("abc", "abcd", False),
        ("a.c", "abc", True),
        ("a*", "", True),
        ("a*b", "aaab", True),
        ("a+b", "b", False),
        ("a?b", "ab", True),
        ("a?b", "b", True),
        ("[a-z]+", "hello", True),
        ("[a-z]+", "Hello", False),
        ("[^abc]*", "xyz", True),
        ("[a-z0-9]+", "ab12", True),
        (".*", "anything at all", True),
    ]
    for pat, txt, expected in tests:
        got = match(pat, txt)
        status = "ok " if got == expected else "FAIL"
        print("%s %r vs %r -> %s" % (status, pat, txt, got))

    for bad in ["*a", "[abc", "a**", "+", "?x", "[]"]:
        try:
            match(bad, "x")
        except ValueError:
            print("ok  %r raised ValueError" % bad)
        else:
            print("FAIL %r did not raise" % bad)
