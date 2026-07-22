#!/usr/bin/env python3
"""
A simple regex matcher supporting a small subset of features:
- literals, dot (.), character classes [abc], ranges [a-z], negated classes [^abc]
- quantifiers *, +, ?
"""

from typing import List, Tuple

# Token types
LITERAL = "LITERAL"
DOT = "DOT"
CLASS = "CLASS"

# Quantifier types
NONE = "NONE"
STAR = "*"
PLUS = "+"
QUESTION = "?"

class Token:
    def __init__(self, typ: str, value=None, quant=NONE):
        self.typ = typ          # LITERAL, DOT, CLASS
        self.value = value      # char for literal, set of chars and negated flag for class
        self.quant = quant

    def __repr__(self):
        return f"Token({self.typ!r}, {self.value!r}, {self.quant!r})"

def parse_pattern(pattern: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]
        if ch == '[':
            # Find closing ]
            end = pattern.find(']', i + 1)
            if end == -1:
                raise ValueError("Unclosed character class")
            content = pattern[i+1:end]
            if not content:
                raise ValueError("Empty character class")
            negated = False
            idx = 0
            char_set = set()
            if content[0] == '^':
                negated = True
                idx = 1
            while idx < len(content):
                c = content[idx]
                if c == '-' and idx > 0 and idx+1 < len(content):
                    start = content[idx-1]
                    end_char = content[idx+1]
                    for code in range(ord(start), ord(end_char)+1):
                        char_set.add(chr(code))
                    idx += 2
                else:
                    char_set.add(c)
                    idx += 1
            token = Token(CLASS, (char_set, negated))
            i = end + 1
        elif ch == '.':
            token = Token(DOT)
            i += 1
        elif ch in ('*', '+', '?'):
            if not tokens:
                raise ValueError(f"Quantifier '{ch}' at start of pattern")
            # Attach quantifier to previous token
            prev = tokens.pop()
            prev.quant = ch
            tokens.append(prev)
            i += 1
            continue  # skip adding new token
        else:
            token = Token(LITERAL, ch)
            i += 1

        # Check for following quantifier
        if i < n and pattern[i] in ('*', '+', '?'):
            token.quant = pattern[i]
            i += 1
        tokens.append(token)

    return tokens

def match_char(token: Token, ch: str) -> bool:
    if token.typ == LITERAL:
        return token.value == ch
    elif token.typ == DOT:
        return True
    elif token.typ == CLASS:
        char_set, negated = token.value
        in_set = ch in char_set
        return not in_set if negated else in_set
    return False

def match_from(tokens: List[Token], text: str, ti: int, pi: int) -> bool:
    if pi == len(tokens):
        return ti == len(text)

    token = tokens[pi]
    quant = token.quant

    if quant == NONE:
        if ti >= len(text):
            return False
        if not match_char(token, text[ti]):
            return False
        return match_from(tokens, text, ti+1, pi+1)
    elif quant == STAR:
        # Try all possible repetitions
        pos = ti
        while True:
            if match_from(tokens, text, pos, pi+1):
                return True
            if pos >= len(text) or not match_char(token, text[pos]):
                break
            pos += 1
        return False
    elif quant == PLUS:
        # Must match at least one
        if ti >= len(text) or not match_char(token, text[ti]):
            return False
        pos = ti + 1
        while True:
            if match_from(tokens, text, pos, pi+1):
                return True
            if pos >= len(text) or not match_char(token, text[pos]):
                break
            pos += 1
        return False
    elif quant == QUESTION:
        # Try zero occurrence
        if match_from(tokens, text, ti, pi+1):
            return True
        # Or one occurrence
        if ti < len(text) and match_char(token, text[ti]):
            return match_from(tokens, text, ti+1, pi+1)
        return False
    else:
        raise ValueError(f"Unknown quantifier {quant}")

def match(pattern: str, text: str) -> bool:
    """
    Return True if the entire `text` matches the regex `pattern`.
    Raises ValueError for malformed patterns.
    """
    tokens = parse_pattern(pattern)
    return match_from(tokens, text, 0, 0)

# Example usage (uncomment to test):
# if __name__ == "__main__":
#     tests = [
#         ("a*b", "aaab", True),
#         ("a+b", "b", False),
#         ("[abc]+", "cab", True),
#         ("[^x]*y", "zzzy", True),
#         (".*", "", True),
#         ("", "", True),
#         ("", "a", False)
#     ]
#     for pat, txt, expected in tests:
#         result = match(pat, txt)
#         print(f"match({pat!r}, {txt!r}) -> {result} (expected {expected})")
