from typing import Set

class Token:
    """Represents a regex token."""
    def __init__(self, typ: str, char: str = None, chars: Set[str] = None,
                 negated: bool = False, quant: str = None):
        self.type = typ          # 'literal', 'dot', 'class'
        self.char = char         # for literal
        self.chars = chars       # for character class
        self.negated = negated   # for character class
        self.quant = quant       # '*', '+', '?' or None


def parse_class(pattern: str, i: int):
    """Parse character class starting at pattern[i] == '['.
    Returns (Token, next_index)."""
    j = i + 1
    if j >= len(pattern):
        raise ValueError("unclosed '['")

    negated = False
    if pattern[j] == '^':
        negated = True
        j += 1
        if j >= len(pattern):
            raise ValueError("unclosed '['")

    chars: Set[str] = set()
    range_start = None  # last single char added, for detecting ranges

    # ']' immediately after (or after '^') is literal
    if j < len(pattern) and pattern[j] == ']':
        chars.add(']')
        range_start = ']'
        j += 1

    while j < len(pattern) and pattern[j] != ']':
        ch = pattern[j]
        if ch == '-':
            # Range if possible: need a start char and a following char other than ']'
            if range_start is not None and (j + 1) < len(pattern) and pattern[j + 1] != ']':
                start = range_start
                end = pattern[j + 1]
                if ord(start) > ord(end):
                    raise ValueError(f"Invalid character range {start}-{end} in class")
                for code in range(ord(start), ord(end) + 1):
                    chars.add(chr(code))
                range_start = end
                j += 2  # skip '-' and end char
            else:
                # literal '-'
                chars.add('-')
                range_start = '-'
                j += 1
        else:
            chars.add(ch)
            range_start = ch
            j += 1

    if j >= len(pattern):
        raise ValueError("unclosed '['")
    # j points to ']'
    if not chars:
        raise ValueError("empty character class")

    token = Token('class', chars=chars, negated=negated)
    return token, j + 1  # skip over ']'


def parse_pattern(pattern: str):
    """Parse the regex pattern into a list of tokens."""
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in '*+?':
            if not tokens:
                raise ValueError("quantifier with no preceding element")
            prev = tokens[-1]
            if prev.quant is not None:
                raise ValueError("multiple quantifiers on the same element")
            prev.quant = c
            i += 1
        elif c == '.':
            tokens.append(Token('dot'))
            i += 1
        elif c == '[':
            token, i = parse_class(pattern, i)
            tokens.append(token)
        else:
            # literal character
            tokens.append(Token('literal', char=c))
            i += 1
    return tokens


def match(pattern: str, text: str) -> bool:
    """
    Returns True if pattern matches the ENTIRE text.
    Supports: literal, ., *, +, ?, character classes [abc], ranges [a-z0-9],
    and negation [^abc].
    """
    tokens = parse_pattern(pattern)

    def match_one(token: Token, txt: str, pos: int) -> bool:
        if pos >= len(txt):
            return False
        if token.type == 'literal':
            return txt[pos] == token.char
        elif token.type == 'dot':
            return True
        elif token.type == 'class':
            in_set = txt[pos] in token.chars
            return not in_set if token.negated else in_set
        else:
            raise ValueError("Unknown token type")

    def match_here(i: int, j: int) -> bool:
        if i == len(tokens):
            return j == len(text)
        token = tokens[i]
        q = token.quant
        if q is None:
            return j < len(text) and match_one(token, text, j) and match_here(i + 1, j + 1)
        elif q == '?':
            # zero or one
            if j < len(text) and match_one(token, text, j):
                if match_here(i + 1, j + 1):
                    return True
            return match_here(i + 1, j)
        elif q == '*':
            # zero or more – try skipping first, then consuming one by one
            if match_here(i + 1, j):
                return True
            while j < len(text) and match_one(token, text, j):
                j += 1
                if match_here(i + 1, j):
                    return True
            return False
        elif q == '+':
            # one or more
            if j >= len(text) or not match_one(token, text, j):
                return False
            j += 1
            while True:
                if match_here(i + 1, j):
                    return True
                if j < len(text) and match_one(token, text, j):
                    j += 1
                else:
                    break
            return False
        else:
            raise ValueError("Unknown quantifier")

    return match_here(0, 0)
