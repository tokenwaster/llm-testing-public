#!/usr/bin/env python3
"""
A simple regex matcher supporting a small subset of features:
  - literal characters
  - '.' (any single character)
  - '*' , '+' , '?' quantifiers applied to the preceding element
  - character classes: [abc], ranges [a-z0-9], negation [^abc]
The matcher checks whether the entire pattern matches the entire text.
"""

from functools import lru_cache

class PatternError(ValueError):
    pass


def _parse_class(pattern, pos):
    """Parse a character class starting at '[' and return (set, is_negated, new_pos)."""
    if pattern[pos] != '[':
        raise PatternError("Expected '['")
    pos += 1
    if pos >= len(pattern):
        raise PatternError("Unclosed '['")

    negated = False
    if pattern[pos] == '^':
        negated = True
        pos += 1

    char_set = set()
    while pos < len(pattern) and pattern[pos] != ']':
        c = pattern[pos]
        # Handle escape? Not required by spec.
        if (pos + 2 < len(pattern)) and pattern[pos+1] == '-':
            start = c
            end = pattern[pos+2]
            if ord(start) > ord(end):
                raise PatternError(f"Invalid range {start}-{end}")
            for code in range(ord(start), ord(end)+1):
                char_set.add(chr(code))
            pos += 3
        else:
            char_set.add(c)
            pos += 1

    if pos >= len(pattern) or pattern[pos] != ']':
        raise PatternError("Unclosed '['")
    return (char_set, negated), pos + 1


def _consume_element(pattern, pos):
    """
    Consume a single element from the pattern starting at pos.
    Returns (elem_type, elem_value, new_pos).
    elem_type: 'LITERAL', 'DOT', 'CLASS'
    elem_value: character for LITERAL, set/negated tuple for CLASS
    """
    if pos >= len(pattern):
        return None, None, pos

    ch = pattern[pos]
    if ch == '.':
        return 'DOT', None, pos + 1
    elif ch == '[':
        cls, new_pos = _parse_class(pattern, pos)
        return 'CLASS', cls, new_pos
    else:
        # literal character (any char except special ones)
        if ch in '*+?':
            raise PatternError(f"Quantifier '{ch}' at position {pos} has no preceding element")
        return 'LITERAL', ch, pos + 1


def match(pattern: str, text: str) -> bool:
    """
    Return True if the entire pattern matches the entire text.
    Raises ValueError for malformed patterns.
    """

    # Empty pattern only matches empty text
    if not pattern:
        return text == ""

    @lru_cache(maxsize=None)
    def _match(pi, ti):
        """Recursive matcher: pi index in pattern, ti index in text."""
        if pi == len(pattern) and ti == len(text):
            return True
        if pi == len(pattern):
            return False

        # Consume current element
        elem_type, elem_value, next_pi = _consume_element(pattern, pi)

        # Check for quantifier following the element
        quant = None
        if next_pi < len(pattern) and pattern[next_pi] in '*+?':
            quant = pattern[next_pi]
            next_pi += 1

        def char_matches(c):
            if elem_type == 'LITERAL':
                return c == elem_value
            elif elem_type == 'DOT':
                return True
            else:  # CLASS
                cls_set, negated = elem_value
                in_set = c in cls_set
                return not in_set if negated else in_set

        # No quantifier: must match exactly one character
        if quant is None:
            if ti < len(text) and char_matches(text[ti]):
                return _match(next_pi, ti + 1)
            return False

        # Quantifiers
        if quant == '*':
            # Try all possible repetitions (including zero)
            # First try zero repetition
            if _match(next_pi, ti):
                return True
            # Then consume one by one as long as matches
            k = ti
            while k < len(text) and char_matches(text[k]):
                if _match(next_pi, k + 1):
                    return True
                k += 1
            return False

        if quant == '+':
            # Must match at least once
            if ti >= len(text) or not char_matches(text[ti]):
                return False
            k = ti + 1
            while True:
                if _match(next_pi, k):
                    return True
                if k < len(text) and char_matches(text[k]):
                    k += 1
                else:
                    break
            return False

        if quant == '?':
            # Zero or one
            if _match(next_pi, ti):
                return True
            if ti < len(text) and char_matches(text[ti]):
                return _match(next_pi, ti + 1)
            return False

    try:
        return _match(0, 0)
    except PatternError as e:
        raise ValueError(str(e)) from None


# If run directly, provide a simple test harness
if __name__ == "__main__":
    tests = [
        ("", "", True),
        ("a", "a", True),
        ("a", "", False),
        (".", "b", True),
        ("[abc]", "b", True),
        ("[a-c]", "d", False),
        ("[^x]", "y", True),
        ("ab*c", "ac", True),
        ("ab*c", "abbc", True),
        ("ab+c", "ac", False),
        ("ab?c", "abc", True),
        ("ab?c", "ac", True),
        ("a[bc]*d", "abcbcd", True),
    ]

    for pat, txt, expected in tests:
        res = match(pat, txt)
        print(f"match({pat!r}, {txt!r}) -> {res} (expected {expected})")
