def match(pattern: str, text: str) -> bool:
    """
    Return True if `pattern` matches the entire `text`.

    Supported regex subset:
      - literal characters
      - .  any single character
      - *  zero or more of the preceding element
      - +  one or more of the preceding element
      - ?  zero or one of the preceding element
      - [abc]   character class
      - [a-z]   character range
      - [^abc]  negated class
    """
    atoms = _parse_pattern(pattern)
    return _match_atoms(atoms, text, 0, 0)


def _parse_pattern(pattern: str):
    atoms = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch == '.':
            atom = ('any',)
            i += 1
        elif ch == '[':
            atom, i = _parse_class(pattern, i)
        elif ch in '*+?':
            raise ValueError(f"quantifier '{ch}' has no preceding element at position {i}")
        else:
            atom = ('lit', ch)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        atoms.append((atom, quant))

    return atoms


def _parse_class(pattern: str, start: int):
    close = pattern.find(']', start + 1)
    if close == -1:
        raise ValueError("unclosed character class")

    content = pattern[start + 1:close]
    if not content:
        raise ValueError("empty character class")

    negated = False
    if content[0] == '^':
        negated = True
        content = content[1:]
        if not content:
            raise ValueError("empty negated character class")

    allowed = _parse_class_content(content)
    return ('class', allowed, negated), close + 1


def _parse_class_content(content: str):
    allowed = set()
    i = 0
    n = len(content)

    while i < n:
        # Detect a range like a-z, 0-9.
        if (
            i + 2 < n
            and content[i + 1] == '-'
            and content[i] not in '-]'
            and content[i + 2] != ']'
        ):
            lo = content[i]
            hi = content[i + 2]
            if lo > hi:
                raise ValueError(f"invalid character range '{lo}-{hi}'")
            for code in range(ord(lo), ord(hi) + 1):
                allowed.add(chr(code))
            i += 3
        else:
            allowed.add(content[i])
            i += 1

    return allowed


def _atom_matches(atom, text: str, pos: int) -> bool:
    if pos >= len(text):
        return False

    ch = text[pos]
    kind = atom[0]

    if kind == 'lit':
        return ch == atom[1]
    if kind == 'any':
        return True
    if kind == 'class':
        _, allowed, negated = atom
        in_class = ch in allowed
        return not in_class if negated else in_class

    raise ValueError("unknown pattern atom")


def _match_atoms(atoms, text: str, p: int, t: int) -> bool:
    if p == len(atoms):
        return t == len(text)

    atom, quant = atoms[p]

    if quant is None:
        if _atom_matches(atom, text, t):
            return _match_atoms(atoms, text, p + 1, t + 1)
        return False

    if quant == '?':
        # Greedy: try one match first, then zero.
        if _atom_matches(atom, text, t):
            if _match_atoms(atoms, text, p + 1, t + 1):
                return True
        return _match_atoms(atoms, text, p + 1, t)

    if quant == '*':
        max_count = 0
        while t + max_count < len(text) and _atom_matches(atom, text, t + max_count):
            max_count += 1
        # Backtrack from the greediest match down to zero.
        for k in range(max_count, -1, -1):
            if _match_atoms(atoms, text, p + 1, t + k):
                return True
        return False

    if quant == '+':
        if not _atom_matches(atom, text, t):
            return False
        max_count = 1
        while t + max_count < len(text) and _atom_matches(atom, text, t + max_count):
            max_count += 1
        for k in range(max_count, 0, -1):
            if _match_atoms(atoms, text, p + 1, t + k):
                return True
        return False

    raise ValueError("unknown quantifier")
