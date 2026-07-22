def match(pattern: str, text: str) -> bool:
    """Return True if pattern matches the entire text using a small regex subset."""
    tokens = _tokenize(pattern)
    return _match_tokens(tokens, 0, text, 0)


def _tokenize(pattern: str):
    """Parse pattern into a list of (matcher, quantifier) tokens.

    matcher(c) -> bool
    quantifier is one of None, '*', '+', '?'
    """
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]
        if ch in '*+?':
            raise ValueError("quantifier without a preceding element")

        if ch == '[':
            chars, negated, i = _parse_char_class(pattern, i)
            atom = _make_class_matcher(chars, negated)
        elif ch == '.':
            atom = lambda c: True
            i += 1
        else:
            literal = ch
            atom = lambda c, lit=literal: c == lit
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append((atom, quant))

    return tokens


def _parse_char_class(pattern: str, start: int):
    """Parse a character class starting at pattern[start] == '['.

    Returns (chars: set, negated: bool, next_index).
    """
    n = len(pattern)
    i = start + 1
    if i >= n:
        raise ValueError("unclosed character class")

    negated = False
    if pattern[i] == '^':
        negated = True
        i += 1

    chars = set()
    prev = None

    while i < n and pattern[i] != ']':
        if (
            pattern[i] == '-'
            and prev is not None
            and i + 1 < n
            and pattern[i + 1] != ']'
        ):
            end_char = pattern[i + 1]
            lo, hi = ord(prev), ord(end_char)
            if lo <= hi:
                for code in range(lo, hi + 1):
                    chars.add(chr(code))
            # reverse ranges add nothing (like Python re)
            prev = None
            i += 2
        else:
            chars.add(pattern[i])
            prev = pattern[i]
            i += 1

    if i >= n or pattern[i] != ']':
        raise ValueError("unclosed character class")

    return chars, negated, i + 1


def _make_class_matcher(chars, negated):
    def matcher(c):
        inside = c in chars
        return (not inside) if negated else inside

    return matcher


def _match_tokens(tokens, ti, text, si):
    """Match tokens[ti:] against text[si:] via recursive backtracking."""
    if ti == len(tokens):
        return si == len(text)

    atom, quant = tokens[ti]

    if quant is None:
        if si < len(text) and atom(text[si]):
            return _match_tokens(tokens, ti + 1, text, si + 1)
        return False

    if quant == '?':
        # one (prefer) then zero
        if si < len(text) and atom(text[si]):
            if _match_tokens(tokens, ti + 1, text, si + 1):
                return True
        return _match_tokens(tokens, ti + 1, text, si)

    if quant == '*':
        # consume maximal run, then backtrack
        j = si
        while j < len(text) and atom(text[j]):
            j += 1
        for k in range(j, si - 1, -1):
            if _match_tokens(tokens, ti + 1, text, k):
                return True
        return False

    if quant == '+':
        j = si
        while j < len(text) and atom(text[j]):
            j += 1
        if j == si:
            return False
        for k in range(j, si, -1):
            if _match_tokens(tokens, ti + 1, text, k):
                return True
        return False

    raise ValueError("unknown quantifier")
