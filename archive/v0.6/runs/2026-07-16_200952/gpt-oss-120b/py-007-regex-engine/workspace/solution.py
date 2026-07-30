# solution.py
"""
Simple regular expression matcher supporting a limited subset:
    literals, ., *, +, ?, character classes with ranges and negation.
The matcher checks whether the entire pattern matches the whole text.
Malformed patterns raise ValueError.
"""

from typing import List, Set


class Token:
    __slots__ = ("type", "value", "negated", "quant")

    def __init__(self, typ: str, value=None, negated: bool = False, quant: str = None):
        self.type = typ          # 'literal', 'dot', 'class'
        self.value = value       # character for literal, set for class
        self.negated = negated   # only for class
        self.quant = quant       # None, '*', '+', '?'

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, neg={self.negated}, q={self.quant!r})"


def _parse_char_class(pat: str, start: int) -> (Set[str], bool, int):
    """
    Parse a character class beginning at pat[start] == '['.
    Returns (char_set, negated, new_index) where new_index points
    to the character after the closing ']'.
    """
    i = start + 1
    n = len(pat)
    if i >= n:
        raise ValueError("Unclosed character class")

    negated = False
    if pat[i] == '^':
        negated = True
        i += 1

    chars: Set[str] = set()
    while i < n and pat[i] != ']':
        if i + 2 < n and pat[i + 1] == '-' and pat[i + 2] != ']':
            # range a-z
            start_c = pat[i]
            end_c = pat[i + 2]
            if ord(start_c) > ord(end_c):
                raise ValueError(f"Invalid range {start_c}-{end_c}")
            for code in range(ord(start_c), ord(end_c) + 1):
                chars.add(chr(code))
            i += 3
        else:
            chars.add(pat[i])
            i += 1

    if i >= n or pat[i] != ']':
        raise ValueError("Unclosed character class")
    return chars, negated, i + 1  # position after ']'


def _tokenize(pattern: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        # Quantifier without preceding element is illegal
        if ch in "*+?":
            raise ValueError(f"Quantifier '{ch}' at position {i} has no preceding element")

        # Parse element
        if ch == '.':
            token = Token('dot')
            i += 1
        elif ch == '[':
            char_set, negated, i = _parse_char_class(pattern, i)
            token = Token('class', char_set, negated)
        else:
            token = Token('literal', ch)
            i += 1

        # Check for quantifier
        if i < n and pattern[i] in "*+?":
            token.quant = pattern[i]
            i += 1

        tokens.append(token)

    return tokens


def _char_matches(c: str, token: Token) -> bool:
    if token.type == 'literal':
        return c == token.value
    if token.type == 'dot':
        return True
    if token.type == 'class':
        in_set = c in token.value
        return not in_set if token.negated else in_set
    return False  # should never happen


def match(pattern: str, text: str) -> bool:
    """
    Return True if the entire pattern matches the entire text,
    according to the supported regex subset.
    """
    tokens = _tokenize(pattern)

    # Recursive backtracking matcher
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def _match(tok_idx: int, txt_idx: int) -> bool:
        if tok_idx == len(tokens):
            return txt_idx == len(text)

        token = tokens[tok_idx]
        quant = token.quant

        # Helper to try matching a single character
        def _match_one(pos: int) -> bool:
            return pos < len(text) and _char_matches(text[pos], token)

        if quant is None:
            # Exactly one occurrence
            if _match_one(txt_idx):
                return _match(tok_idx + 1, txt_idx + 1)
            return False

        if quant == '?':
            # Zero occurrence
            if _match(tok_idx + 1, txt_idx):
                return True
            # One occurrence
            if _match_one(txt_idx):
                return _match(tok_idx + 1, txt_idx + 1)
            return False

        if quant == '*':
            # Zero occurrence
            if _match(tok_idx + 1, txt_idx):
                return True
            # One or more occurrences
            pos = txt_idx
            while pos < len(text) and _char_matches(text[pos], token):
                pos += 1
                if _match(tok_idx + 1, pos):
                    return True
            return False

        if quant == '+':
            # Must have at least one
            if not _match_one(txt_idx):
                return False
            pos = txt_idx + 1
            # After the mandatory first, behave like '*'
            if _match(tok_idx + 1, pos):
                return True
            while pos < len(text) and _char_matches(text[pos], token):
                pos += 1
                if _match(tok_idx + 1, pos):
                    return True
            return False

        # Should never reach here
        return False

    return _match(0, 0)
