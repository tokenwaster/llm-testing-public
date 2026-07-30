def match(pattern: str, text: str) -> bool:
    """Return True if pattern matches the entire text using a small regex subset."""
    tokens = _parse(pattern)
    return _match(tokens, 0, text, 0)


def _parse(pattern: str):
    """Parse pattern into a list of (element, quantifier) tokens.

    element is one of:
      ('lit', ch)
      ('dot',)
      ('class', negated: bool, chars: frozenset)
    quantifier is '1' | '*' | '+' | '?'
    """
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]
        if ch in '*+?':
            raise ValueError("quantifier without preceding element")

        if ch == '[':
            elem, i = _parse_class(pattern, i)
        elif ch == '.':
            elem = ('dot',)
            i += 1
        else:
            elem = ('lit', ch)
            i += 1

        quant = '1'
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append((elem, quant))

    return tokens


def _parse_class(pattern: str, start: int):
    """Parse a character class starting at pattern[start] == '['."""
    i = start + 1
    n = len(pattern)
    if i >= n:
        raise ValueError("unclosed character class")

    negated = False
    if pattern[i] == '^':
        negated = True
        i += 1
        if i >= n:
            raise ValueError("unclosed character class")

    chars = set()
    first = True
    closed = False

    while i < n:
        if pattern[i] == ']' and not first:
            closed = True
            i += 1
            break
        first = False

        # Range: X-Y (Y not ']')
        if i + 2 < n and pattern[i + 1] == '-' and pattern[i + 2] != ']':
            lo = ord(pattern[i])
            hi = ord(pattern[i + 2])
            if lo <= hi:
                for code in range(lo, hi + 1):
                    chars.add(chr(code))
            i += 3
        else:
            chars.add(pattern[i])
            i += 1

    if not closed:
        raise ValueError("unclosed character class")

    return ('class', negated, frozenset(chars)), i


def _elem_matches(elem, ch: str) -> bool:
    kind = elem[0]
    if kind == 'lit':
        return elem[1] == ch
    if kind == 'dot':
        return True
    # class
    negated, chars = elem[1], elem[2]
    inside = ch in chars
    return (not inside) if negated else inside


def _match(tokens, ti: int, text: str, si: int) -> bool:
    """Recursive backtracking match from tokens[ti:] against text[si:]."""
    if ti == len(tokens):
        return si == len(text)

    elem, quant = tokens[ti]

    if quant == '1':
        if si < len(text) and _elem_matches(elem, text[si]):
            return _match(tokens, ti + 1, text, si + 1)
        return False

    if quant == '?':
        # zero
        if _match(tokens, ti + 1, text, si):
            return True
        # one
        if si < len(text) and _elem_matches(elem, text[si]):
            return _match(tokens, ti + 1, text, si + 1)
        return False

    if quant == '*':
        return _match_star(elem, tokens, ti + 1, text, si)

    if quant == '+':
        if si < len(text) and _elem_matches(elem, text[si]):
            return _match_star(elem, tokens, ti + 1, text, si + 1)
        return False

    raise ValueError("unknown quantifier")


def _match_star(elem, tokens, ti: int, text: str, si: int) -> bool:
    """Match zero-or-more of elem at text[si:], then tokens[ti:]."""
    # Collect all end-positions after k matches of elem (k = 0, 1, 2, ...)
    positions = [si]
    j = si
    while j < len(text) and _elem_matches(elem, text[j]):
        j += 1
        positions.append(j)

    # Try longest first (greedy backtracking)
    for pos in reversed(positions):
        if _match(tokens, ti, text, pos):
            return True
    return False
