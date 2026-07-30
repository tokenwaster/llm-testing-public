def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match_here(tokens, 0, text, 0)


def _parse(pattern):
    """Parse pattern into a list of (matcher, quantifier) tuples.

    matcher is a callable char -> bool.
    quantifier is one of '', '*', '+', '?'.
    Raises ValueError on malformed patterns.
    """
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '*' or c == '+' or c == '?':
            raise ValueError("quantifier with nothing to repeat at position %d" % i)
        if c == '.':
            matcher = _any_matcher()
            i += 1
        elif c == '[':
            matcher, i = _parse_class(pattern, i)
        else:
            matcher = _literal_matcher(c)
            i += 1

        quant = ''
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        tokens.append((matcher, quant))
    return tokens


def _any_matcher():
    return lambda ch: True


def _literal_matcher(c):
    return lambda ch: ch == c


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.

    Returns (matcher, next_index). Raises ValueError if unclosed.
    """
    n = len(pattern)
    assert pattern[i] == '['
    j = i + 1
    negate = False
    if j < n and pattern[j] == '^':
        negate = True
        j += 1

    members = []  # list of ('char', c) or ('range', lo, hi)
    found_close = False
    while j < n:
        if pattern[j] == ']':
            found_close = True
            break
        # Check for a range: X-Y where Y is not ']'
        if (j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']'):
            lo = pattern[j]
            hi = pattern[j + 2]
            if lo > hi:
                raise ValueError("invalid range %s-%s in class" % (lo, hi))
            members.append(('range', lo, hi))
            j += 3
        else:
            members.append(('char', pattern[j]))
            j += 1

    if not found_close:
        raise ValueError("unclosed character class")
    if not members:
        raise ValueError("empty character class")

    # j points at ']'
    next_index = j + 1

    def matcher(ch):
        result = False
        for m in members:
            if m[0] == 'char':
                if ch == m[1]:
                    result = True
                    break
            else:
                if m[1] <= ch <= m[2]:
                    result = True
                    break
        return result != negate

    return matcher, next_index


def _match_here(tokens, ti, text, si):
    """Try to match tokens[ti:] against text[si:], anchored at both ends."""
    if ti == len(tokens):
        return si == len(text)

    matcher, quant = tokens[ti]

    if quant == '':
        if si < len(text) and matcher(text[si]):
            return _match_here(tokens, ti + 1, text, si + 1)
        return False

    if quant == '?':
        # Try one, then zero.
        if si < len(text) and matcher(text[si]):
            if _match_here(tokens, ti + 1, text, si + 1):
                return True
        return _match_here(tokens, ti + 1, text, si)

    if quant == '*':
        # Greedy: consume as many as possible, backtrack.
        count = 0
        while si + count < len(text) and matcher(text[si + count]):
            count += 1
        for k in range(count, -1, -1):
            if _match_here(tokens, ti + 1, text, si + k):
                return True
        return False

    if quant == '+':
        count = 0
        while si + count < len(text) and matcher(text[si + count]):
            count += 1
        for k in range(count, 0, -1):
            if _match_here(tokens, ti + 1, text, si + k):
                return True
        return False

    raise ValueError("unknown quantifier %r" % quant)
