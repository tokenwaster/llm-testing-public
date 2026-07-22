def match(pattern: str, text: str) -> bool:
    # Parse the pattern into a list of atoms.
    # Each atom is a tuple: (type, value, quantifier)
    # type: 'lit', 'dot', or 'class'
    # value: char for 'lit', None for 'dot', (neg, set) for 'class'
    # quantifier: None, '*', '+', or '?'
    atoms = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in '*+?':
            raise ValueError("quantifier with nothing before it")
        if c == '.':
            atom_type = 'dot'
            atom_val = None
            i += 1
        elif c == '[':
            i += 1
            neg = False
            if i < n and pattern[i] == '^':
                neg = True
                i += 1
            chars = set()
            while i < n and pattern[i] != ']':
                if i + 2 < n and pattern[i + 1] == '-' and pattern[i + 2] != ']':
                    start = pattern[i]
                    end = pattern[i + 2]
                    if start > end:
                        raise ValueError("invalid range in character class")
                    for o in range(ord(start), ord(end) + 1):
                        chars.add(chr(o))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            if i >= n:
                raise ValueError("unclosed character class")
            i += 1  # consume closing ']'
            atom_type = 'class'
            atom_val = (neg, chars)
        else:
            atom_type = 'lit'
            atom_val = c
            i += 1
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        atoms.append((atom_type, atom_val, quant))

    def matches_char(atom, ch):
        typ, val, _ = atom
        if typ == 'dot':
            return True
        elif typ == 'lit':
            return ch == val
        elif typ == 'class':
            neg, chars = val
            return (ch not in chars) if neg else (ch in chars)
        return False

    def match_suffix(idx, pos):
        if idx == len(atoms):
            return pos == len(text)
        atom = atoms[idx]
        _, _, quant = atom
        rem = len(text) - pos
        if quant == '*':
            min_rep, max_rep = 0, rem
        elif quant == '+':
            min_rep, max_rep = 1, rem
        elif quant == '?':
            min_rep, max_rep = 0, min(1, rem)
        else:
            min_rep, max_rep = 1, rem

        for k in range(min_rep, max_rep + 1):
            ok = True
            for offset in range(k):
                if not matches_char(atom, text[pos + offset]):
                    ok = False
                    break
            if not ok:
                break
            if match_suffix(idx + 1, pos + k):
                return True
        return False

    return match_suffix(0, 0)
