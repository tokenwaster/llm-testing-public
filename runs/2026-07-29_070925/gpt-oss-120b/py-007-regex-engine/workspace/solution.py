"""
solution.py

Implements a simple regular expression engine that supports:
    literals, ., *, +, ?, character classes with ranges and negation.
The match() function returns True iff the whole pattern matches the whole text.
Malformed patterns raise ValueError.
"""

from __future__ import annotations
from typing import List, Dict


def _parse_pattern(pat: str) -> List[Dict]:
    """
    Convert pattern string into a list of token dictionaries.
    Each token has keys:
        kind : 'literal' | 'dot' | 'class'
        val  : depends on kind (character, (set,negated), None)
        quant: None | '*' | '+' | '?'
    Raises ValueError on malformed patterns.
    """
    i = 0
    n = len(pat)
    tokens: List[Dict] = []

    while i < n:
        c = pat[i]

        # ----- literal dot -----
        if c == ".":
            kind = "dot"
            val = None
            i += 1

        # ----- character class -----
        elif c == "[":
            i += 1
            if i >= n:
                raise ValueError("unterminated character class")

            neg = False
            if pat[i] == "^":
                neg = True
                i += 1

            chars = set()
            while i < n and pat[i] != "]":
                # range a-z ?
                if (
                    i + 2 < n
                    and pat[i + 1] == "-"
                    and pat[i + 2] != "]"
                ):
                    start, end = pat[i], pat[i + 2]
                    if ord(start) > ord(end):
                        raise ValueError(f"invalid range {start}-{end}")
                    for cp in range(ord(start), ord(end) + 1):
                        chars.add(chr(cp))
                    i += 3
                else:
                    chars.add(pat[i])
                    i += 1

            if i >= n or pat[i] != "]":
                raise ValueError("unterminated character class")
            i += 1  # skip closing ]

            kind = "class"
            val = (chars, neg)

        # ----- quantifier without atom -----
        elif c in "*+?":
            raise ValueError(f"quantifier '{c}' at position {i} has no preceding atom")

        # ----- ordinary literal -----
        else:
            kind = "literal"
            val = c
            i += 1

        # ----- optional quantifier after the atom -----
        quant = None
        if i < n and pat[i] in "*+?":
            quant = pat[i]
            i += 1

        tokens.append({"kind": kind, "val": val, "quant": quant})

    return tokens


def _token_matches(tok: Dict, ch: str) -> bool:
    """Check whether a single token matches a single character."""
    kind = tok["kind"]
    if kind == "dot":
        return True
    if kind == "literal":
        return tok["val"] == ch
    if kind == "class":
        chars, neg = tok["val"]
        return (ch not in chars) if neg else (ch in chars)
    return False  # unreachable


def match(pattern: str, text: str) -> bool:
    """
    Return True iff the entire ``pattern`` matches the entire ``text``.
    Supported constructs: literals, '.', '*', '+', '?',
    character classes with ranges and negation.
    Raises ValueError for malformed patterns.
    """
    # Empty pattern matches only empty text.
    if pattern == "":
        return text == ""

    tokens = _parse_pattern(pattern)
    txt_len = len(text)

    # Recursive backtracking matcher
    def dfs(p_idx: int, t_idx: int) -> bool:
        if p_idx == len(tokens):
            return t_idx == txt_len

        tok = tokens[p_idx]
        q = tok["quant"]

        # ----- No quantifier (exactly one) -----
        if q is None:
            if t_idx < txt_len and _token_matches(tok, text[t_idx]):
                return dfs(p_idx + 1, t_idx + 1)
            return False

        # ----- Zero-or-one (optional) -----
        if q == "?":
            # Try zero occurrences first
            if dfs(p_idx + 1, t_idx):
                return True
            # Then one occurrence
            if t_idx < txt_len and _token_matches(tok, text[t_idx]):
                return dfs(p_idx + 1, t_idx + 1)
            return False

        # ----- Zero-or-more (greedy with backtrack) -----
        if q == "*":
            # Consume as many as possible
            k = t_idx
            while k < txt_len and _token_matches(tok, text[k]):
                k += 1
            # Try from longest stretch down to zero
            for nxt in range(k, t_idx - 1, -1):
                if dfs(p_idx + 1, nxt):
                    return True
            return False

        # ----- One-or-more -----
        if q == "+":
            # Need at least one
            if t_idx >= txt_len or not _token_matches(tok, text[t_idx]):
                return False
            k = t_idx + 1
            while k < txt_len and _token_matches(tok, text[k]):
                k += 1
            # Try all possibilities (greedy)
            for nxt in range(k, t_idx, -1):
                if dfs(p_idx + 1, nxt):
                    return True
            return False

        # Should never reach here
        return False

    return dfs(0, 0)
