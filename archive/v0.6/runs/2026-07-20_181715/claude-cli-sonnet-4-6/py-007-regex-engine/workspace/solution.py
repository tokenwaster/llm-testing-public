def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match(tokens, 0, text, 0)


def _parse(pattern):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in '*+?':
            raise ValueError(f"Quantifier '{c}' at position {i} has no preceding element")
        elif c == '[':
            i, elem = _parse_class(pattern, i)
        elif c == '.':
            elem = ('dot',)
            i += 1
        else:
            elem = ('lit', c)
            i += 1

        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        else:
            quant = None

        tokens.append((elem, quant))
    return tokens


def _parse_class(pattern, start):
    j = start + 1
    n = len(pattern)
    negated = False
    if j < n and pattern[j] == '^':
        negated = True
        j += 1
    chars = set()
    while j < n and pattern[j] != ']':
        if j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']':
            lo, hi = pattern[j], pattern[j + 2]
            if ord(lo) > ord(hi):
                raise ValueError(f"Invalid character range '{lo}-{hi}'")
            for code in range(ord(lo), ord(hi) + 1):
                chars.add(chr(code))
            j += 3
        else:
            chars.add(pattern[j])
            j += 1
    if j >= n:
        raise ValueError("Unclosed '[' in pattern")
    return j + 1, ('class', chars, negated)


def _elem_matches(elem, ch):
    kind = elem[0]
    if kind == 'lit':
        return ch == elem[1]
    if kind == 'dot':
        return True
    # 'class': elem = ('class', chars_set, negated)
    in_class = ch in elem[1]
    return in_class != elem[2]


def _match(tokens, ti, text, si):
    if ti == len(tokens):
        return si == len(text)

    elem, quant = tokens[ti]

    if quant is None:
        if si >= len(text) or not _elem_matches(elem, text[si]):
            return False
        return _match(tokens, ti + 1, text, si + 1)

    if quant == '?':
        if _match(tokens, ti + 1, text, si):
            return True
        if si < len(text) and _elem_matches(elem, text[si]):
            return _match(tokens, ti + 1, text, si + 1)
        return False

    # Collect consecutive positions where elem matches
    positions = [] if quant == '+' else [si]
    pos = si
    while pos < len(text) and _elem_matches(elem, text[pos]):
        pos += 1
        positions.append(pos)

    # quant == '+' requires at least one match, so positions is non-empty only if we matched
    for p in reversed(positions):
        if _match(tokens, ti + 1, text, p):
            return True
    return False
