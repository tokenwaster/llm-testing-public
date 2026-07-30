#!/usr/bin/env python3
"""
A simple regular expression matcher supporting a small subset of regex syntax:
- literal characters
- '.' (any single character)
- '*' (zero or more of the preceding element)
- '+' (one or more of the preceding element)
- '?' (zero or one of the preceding element)
- character classes [abc], ranges [a-z0-9] and negation [^abc]
  with optional quantifiers (*, +, ?) following a class.
"""

from functools import lru_cache
from typing import Callable, List, Tuple


class Token:
    """Represents a single regex token (element) and an optional quantifier."""
    def __init__(self, match_func: Callable[[str], bool], quant: str | None):
        self.match = match_func
        self.quant = quant  # None, '*', '+', or '?'


def _parse_pattern(pattern: str) -> List[Token]:
    """Convert the pattern string into a list of Tokens. Raise ValueError on malformed patterns."""
    tokens: List[Token] = []
    i = 0
    n = len(pattern)

    while i < n:
        # Parse an element (literal, dot or character class)
        if pattern[i] == '[':
            elem_func, new_i = _parse_class(pattern, i)
            i = new_i
        elif pattern[i] == '.':
            elem_func = lambda c: True  # any single char
            i += 1
        else:
            # literal character (any character except special ones)
            if pattern[i] in '*+?':
                raise ValueError(f"Quantifier '{pattern[i]}' at position {i} has nothing before it")
            elem_func = lambda c, ch=pattern[i]: c == ch
            i += 1

        # Check for an optional quantifier following the element
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append(Token(elem_func, quant))

    return tokens


def _parse_class(pattern: str, start_i: int) -> Tuple[Callable[[str], bool], int]:
    """Parse a character class starting at '['. Return a matching function and new index after ']'."""
    assert pattern[start_i] == '[', "Expected '[' at the start of a character class"
    i = start_i + 1
    n = len(pattern)
    if i >= n:
        raise ValueError(f"Unclosed '[' starting at position {start_i}")

    negated = False
    if pattern[i] == '^':
        negated = True
        i += 1

    char_set = set()
    prev_char = None
    while i < n and pattern[i] != ']':
        ch = pattern[i]
        if ch == '-' and prev_char is not None and i + 1 < n and pattern[i + 1] != ']':
            # Range: prev_char - next_char
            end_ch = pattern[i + 1]
            for code in range(ord(prev_char), ord(end_ch) + 1):
                char_set.add(chr(code))
            i += 2
            prev_char = None
        else:
            char_set.add(ch)
            prev_char = ch
            i += 1

    if i >= n or pattern[i] != ']':
        raise ValueError(f"Unclosed '[' starting at position {start_i}")

    # Create matching function based on set and negation
    if negated:
        match_func = lambda c, s=char_set: c not in s
    else:
        match_func = lambda c, s=char_set: c in s

    return match_func, i + 1


def match(pattern: str, text: str) -> bool:
    """
    Return True if the entire pattern matches the entire text according to the rules.
    Raises ValueError on malformed patterns.
    """
    tokens = _parse_pattern(pattern)

    @lru_cache(maxsize=None)
    def rec(ti: int, ji: int) -> bool:
        # If we consumed all tokens and all text, it's a match
        if ti == len(tokens):
            return ji == len(text)

        token = tokens[ti]
        quant = token.quant

        # Helper to attempt matching the next token
        def try_next(skip_count: int = 0) -> bool:
            return rec(ti + skip_count, ji)

        if quant is None:
            # Must match exactly one character
            if ji < len(text) and token.match(text[ji]):
                return rec(ti + 1, ji + 1)
            return False

        if quant == '*':
            # Zero occurrences
            if try_next():
                return True
            # One or more: consume characters while they match
            k = ji
            while k < len(text) and token.match(text[k]):
                if rec(ti, k + 1):
                    return True
                k += 1
            return False

        if quant == '+':
            # At least one occurrence
            if ji >= len(text) or not token.match(text[ji]):
                return False
            k = ji
            while k < len(text) and token.match(text[k]):
                # After consuming at least one, try to stay on this token (for more repeats)
                if rec(ti, k + 1):
                    return True
                k += 1
            return False

        if quant == '?':
            # Zero occurrences
            if try_next():
                return True
            # One occurrence
            if ji < len(text) and token.match(text[ji]):
                return rec(ti + 1, ji + 1)
            return False

        # Should never reach here
        raise ValueError(f"Unsupported quantifier: {quant}")

    return rec(0, 0)
