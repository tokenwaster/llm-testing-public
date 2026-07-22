"""A small regex matcher supporting literals, '.', '*', '+', '?', and
character classes ([abc], [a-z0-9], [^abc]). Matches the ENTIRE text.
"""


class _CharClass:
    def __init__(self, chars, negated):
        self.chars = chars      # frozenset of characters
        self.negated = negated

    def matches(self, ch):
        return (ch not in self.chars) if self.negated else (ch in self.chars)


class _Dot:
    def matches(self, ch):
        return True


class _Literal:
    def __init__(self, ch):
        self.ch = ch

    def matches(self, ch):
        return ch == self.ch


_QUANTIFIERS = {'*', '+', '?'}


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.
    Returns (element, next_index)."""
    j = i + 1
    negated = False
    if j < len(pattern) and pattern[j] == '^':
        negated = True
        j += 1

    chars = set()
    while j < len(pattern) and pattern[j] != ']':
        ch = pattern[j]
        # Range like a-z: a '-' with a valid endpoint on each side and
        # the right endpoint not being the closing ']'.
        if (j + 2 < len(pattern) and pattern[j + 1] == '-'
                and pattern[j + 2] != ']'):
            lo, hi = ch, pattern[j + 2]
            if ord(lo) > ord(hi):
                raise ValueError(
                    f"invalid range {lo}-{hi} in character class")
            for code in range(ord(lo), ord(hi) + 1):
                chars.add(chr(code))
            j += 3
        else:
            chars.add(ch)
            j += 1

    if j >= len(pattern):
        raise ValueError("unclosed '[' in pattern")
    if not chars:
        raise ValueError("empty character class")
    return _CharClass(frozenset(chars), negated), j + 1


def _parse(pattern):
    """Tokenize into a list of (element, quantifier) pairs, where
    quantifier is one of None, '*', '?' ('+' is rewritten as X X*)."""
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch in _QUANTIFIERS:
            raise ValueError(
                f"quantifier '{ch}' with no preceding element at position {i}")
        if ch == '[':
            elem, i = _parse_class(pattern, i)
        elif ch == '.':
            elem = _Dot()
            i += 1
        else:
            elem = _Literal(ch)
            i += 1

        quant = None
        if i < len(pattern) and pattern[i] in _QUANTIFIERS:
            quant = pattern[i]
            i += 1
            if i < len(pattern) and pattern[i] in _QUANTIFIERS:
                raise ValueError(
                    f"quantifier '{pattern[i]}' with no preceding element "
                    f"at position {i}")

        if quant == '+':
            # X+  ==  X X*
            tokens.append((elem, None))
            tokens.append((elem, '*'))
        else:
            tokens.append((elem, quant))
    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    memo = {}

    def rec(ti, si):
        key = (ti, si)
        if key in memo:
            return memo[key]
        if ti == len(tokens):
            result = si == len(text)
        else:
            elem, quant = tokens[ti]
            can_consume = si < len(text) and elem.matches(text[si])
            if quant is None:
                result = can_consume and rec(ti + 1, si + 1)
            elif quant == '?':
                result = rec(ti + 1, si) or (can_consume and rec(ti + 1, si + 1))
            else:  # '*'
                result = rec(ti + 1, si) or (can_consume and rec(ti, si + 1))
        memo[key] = result
        return result

    return rec(0, 0)
