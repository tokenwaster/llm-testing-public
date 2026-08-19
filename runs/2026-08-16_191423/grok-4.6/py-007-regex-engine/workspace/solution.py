def match(pattern: str, text: str) -> bool:
    """Return True iff pattern matches the entire text."""
    atoms = _parse(pattern)
    return _match(atoms, 0, text, 0)


def _parse(pattern: str):
    """Parse pattern into a list of (kind, data, quant) atoms.

    kind is 'lit', 'dot', or 'cls'.
    quant is None, '*', '+', or '?'.
    """
    atoms = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch in '*+?':
            raise ValueError('quantifier with no preceding element')
        if ch == '[':
            i, atom = _parse_class(pattern, i)
        elif ch == '.':
            atom = ('dot', None)
            i += 1
        else:
            atom = ('lit', ch)
            i += 1
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        atoms.append((atom[0], atom[1], quant))
    return atoms


def _parse_class(pattern: str, start: int):
    """Parse a character class beginning at pattern[start] == '['.

    Returns (index_after_class, ('cls', (negated, frozenset))).
    """
    n = len(pattern)
    i = start + 1
    if i >= n:
        raise ValueError('unclosed character class')

    negated = False
    if pattern[i] == '^':
        negated = True
        i += 1
        if i >= n:
            raise ValueError('unclosed character class')

    chars = set()
    # ']' immediately after '[' or '[^' is a literal ']'
    if pattern[i] == ']':
        chars.add(']')
        i += 1

    while i < n and pattern[i] != ']':
        # range a-b, but '-' before ']' is literal
        if (
            i + 2 < n
            and pattern[i + 1] == '-'
            and pattern[i + 2] != ']'
        ):
            lo = pattern[i]
            hi = pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError('bad character range')
            for code in range(ord(lo), ord(hi) + 1):
                chars.add(chr(code))
            i += 3
        else:
            chars.add(pattern[i])
            i += 1

    if i >= n or pattern[i] != ']':
        raise ValueError('unclosed character class')
    i += 1
    return i, ('cls', (negated, frozenset(chars)))


def _atom_matches(kind, data, ch: str) -> bool:
    if kind == 'lit':
        return ch == data
    if kind == 'dot':
        return True
    negated, chars = data
    inside = ch in chars
    return (not inside) if negated else inside


def _match(atoms, ai: int, text: str, ti: int) -> bool:
    if ai == len(atoms):
        return ti == len(text)

    kind, data, quant = atoms[ai]

    def one(pos: int) -> bool:
        return pos < len(text) and _atom_matches(kind, data, text[pos])

    if quant is None:
        return one(ti) and _match(atoms, ai + 1, text, ti + 1)

    if quant == '?':
        if _match(atoms, ai + 1, text, ti):
            return True
        return one(ti) and _match(atoms, ai + 1, text, ti + 1)

    if quant == '*':
        # zero or more (consume one char at a time, then stay on this atom)
        if _match(atoms, ai + 1, text, ti):
            return True
        return one(ti) and _match(atoms, ai, text, ti + 1)

    # quant == '+'
    if not one(ti):
        return False
    if _match(atoms, ai + 1, text, ti + 1):
        return True
    return _match(atoms, ai, text, ti + 1)
