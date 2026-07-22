def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match_tokens(tokens, 0, text, 0)


def _parse(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        atom, i = _parse_atom(pattern, i)
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in '*+?':
                raise ValueError(
                    f"multiple quantifiers in pattern: {pattern!r}"
                )
        tokens.append((atom, quant))
    return tokens


def _parse_atom(pattern: str, i: int):
    c = pattern[i]
    if c == '[':
        j = i + 1
        negate = False
        if j < len(pattern) and pattern[j] == '^':
            negate = True
            j += 1
        if j >= len(pattern):
            raise ValueError(
                f"unclosed character class in pattern: {pattern!r}"
            )
        chars = set()
        while j < len(pattern) and pattern[j] != ']':
            if (j + 2 < len(pattern)
                    and pattern[j + 1] == '-'
                    and pattern[j + 2] != ']'):
                start = pattern[j]
                end = pattern[j + 2]
                if ord(start) > ord(end):
                    raise ValueError(
                        f"bad range {start!r}-{end!r} in pattern: {pattern!r}"
                    )
                for k in range(ord(start), ord(end) + 1):
                    chars.add(chr(k))
                j += 3
            else:
                chars.add(pattern[j])
                j += 1
        if j >= len(pattern):
            raise ValueError(
                f"unclosed character class in pattern: {pattern!r}"
            )
        j += 1
        return ('class', frozenset(chars), negate), j
    if c == '.':
        return ('wildcard',), i + 1
    if c in '*+?':
        raise ValueError(
            f"nothing to repeat at position {i} in pattern: {pattern!r}"
        )
    return ('char', c), i + 1


def _atom_matches(atom, c: str) -> bool:
    kind = atom[0]
    if kind == 'char':
        return atom[1] == c
    if kind == 'class':
        return (c in atom[1]) != atom[2]
    return True


def _match_tokens(tokens, ti: int, text: str, si: int) -> bool:
    if ti == len(tokens):
        return si == len(text)
    atom, quant = tokens[ti]
    if quant is None:
        if si >= len(text):
            return False
        if not _atom_matches(atom, text[si]):
            return False
        return _match_tokens(tokens, ti + 1, text, si + 1)
    if quant == '?':
        if _match_tokens(tokens, ti + 1, text, si):
            return True
        if si < len(text) and _atom_matches(atom, text[si]):
            return _match_tokens(tokens, ti + 1, text, si + 1)
        return False
    if quant == '*':
        if _match_tokens(tokens, ti + 1, text, si):
            return True
        i = si
        while i < len(text) and _atom_matches(atom, text[i]):
            i += 1
            if _match_tokens(tokens, ti + 1, text, i):
                return True
        return False
    if si >= len(text) or not _atom_matches(atom, text[si]):
        return False
    i = si + 1
    while True:
        if _match_tokens(tokens, ti + 1, text, i):
            return True
        if i >= len(text) or not _atom_matches(atom, text[i]):
            break
        i += 1
    return False
