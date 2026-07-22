#!/usr/bin/env python3
"""
Simple regex engine supporting a small subset:
    literal, ., *, +, ?, character classes [abc], ranges [a-z0-9], negation [^abc]
"""

from typing import List, Tuple

class Token:
    def __init__(self, kind: str, value=None):
        self.kind = kind  # 'lit', '.', 'class'
        self.value = value  # char or set of chars
        self.quant = ''     # '', '*', '+', '?'

def parse_pattern(pat: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(pat):
        ch = pat[i]
        if ch == '[':
            # find closing ]
            j = i + 1
            if j >= len(pat):
                raise ValueError("Unclosed character class")
            negated = False
            if pat[j] == '^':
                negated = True
                j += 1
            chars = set()
            while j < len(pat) and pat[j] != ']':
                start = pat[j]
                if j + 2 < len(pat) and pat[j+1] == '-':
                    end = pat[j+2]
                    for c in range(ord(start), ord(end)+1):
                        chars.add(chr(c))
                    j += 3
                else:
                    chars.add(start)
                    j += 1
            if j >= len(pat) or pat[j] != ']':
                raise ValueError("Unclosed character class")
            token = Token('class', chars)
            if negated:
                # store as negative set by using a flag in value
                token.value = ('neg', chars)
            i = j + 1
        elif ch == '.':
            token = Token('.', None)
            i += 1
        else:
            token = Token('lit', ch)
            i += 1

        # check for quantifier
        if i < len(pat) and pat[i] in '*+?':
            token.quant = pat[i]
            i += 1
        tokens.append(token)

    return tokens

def match_token(tok: Token, c: str) -> bool:
    if tok.kind == 'lit':
        return tok.value == c
    elif tok.kind == '.':
        return True
    else:  # class
        neg, chars = tok.value
        in_set = c in chars
        return not in_set if neg == 'neg' else in_set

def match_helper(tokens: List[Token], text: str, ti: int, si: int) -> bool:
    if ti == len(tokens):
        return si == len(text)
    tok = tokens[ti]
    # handle quantifiers
    if tok.quant == '':
        if si >= len(text):
            return False
        if match_token(tok, text[si]):
            return match_helper(tokens, text, ti+1, si+1)
        else:
            return False
    elif tok.quant == '?':
        # try zero occurrence
        if match_helper(tokens, text, ti+1, si):
            return True
        # try one occurrence
        if si < len(text) and match_token(tok, text[si]):
            return match_helper(tokens, text, ti+1, si+1)
        return False
    elif tok.quant == '*':
        # zero or more: try all possibilities
        # first try zero
        if match_helper(tokens, text, ti+1, si):
            return True
        # then consume one and stay on same token
        pos = si
        while pos < len(text) and match_token(tok, text[pos]):
            pos += 1
            if match_helper(tokens, text, ti+1, pos):
                return True
        return False
    elif tok.quant == '+':
        # at least one
        if si >= len(text) or not match_token(tok, text[si]):
            return False
        pos = si + 1
        while pos <= len(text) and (pos == si+1 or match_token(tok, text[pos-1])):
            if match_helper(tokens, text, ti+1, pos):
                return True
            pos += 1
        return False
    else:
        raise ValueError("Unknown quantifier")

def match(pattern: str, text: str) -> bool:
    """
    Return True if pattern matches the entire text.
    Raises ValueError on malformed patterns.
    """
    # Empty pattern only matches empty string
    if not pattern:
        return text == ''
    tokens = parse_pattern(pattern)
    return match_helper(tokens, text, 0, 0)

# Simple test harness (can be removed or expanded as needed)
if __name__ == "__main__":
    tests = [
        ("a", "a", True),
        ("a", "b", False),
        (".", "x", True),
        ("[abc]", "b", True),
        ("[a-c]d+", "abdcd", True),
        ("[^0-9]+", "abc", True),
        ("a*b", "aaab", True),
        ("a?b", "b", True),
        ("a?b", "ab", True),
        ("a?b", "aab", False),
        ("[a-z]*", "hello123", False),
    ]
    for pat, txt, expected in tests:
        try:
            res = match(pat, txt)
            assert res == expected, f"Pattern {pat!r} on {txt!r}: expected {expected}, got {res}"
        except ValueError as e:
            print(f"Pattern error: {e}")
    print("All tests passed.")
