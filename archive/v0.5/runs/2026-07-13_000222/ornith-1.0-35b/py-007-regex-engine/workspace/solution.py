def match(pattern: str, text: str) -> bool:
    tokens = parse_pattern(pattern)
    return _match(tokens, text, 0, 0)


def parse_pattern(pattern):
    tokens = []
    i = 0
    while i < len(pattern):
        c = pattern[i]

        if c in '*+?':
            raise ValueError(f"Malformed pattern: '{c}' with nothing before it")

        atom = None
        if c == '.':
            atom = ('dot',)
            i += 1
        elif c == '[':
            j = i + 1
            negated = False
            if j < len(pattern) and pattern[j] == '^':
                negated = True
                j += 1

            chars = set()
            first = True
            while j < len(pattern) and (pattern[j] != ']' or first):
                first = False
                if j + 2 < len(pattern) and pattern[j + 1] == '-':
                    start_char = pattern[j]
                    end_char = pattern[j + 2]
                    for code in range(ord(start_char), ord(end_char) + 1):
                        chars.add(chr(code))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1

            if j >= len(pattern):
                raise ValueError("Malformed pattern: unclosed '['")

            atom = ('class', frozenset(chars), negated)
            i = j + 1
        else:
            atom = ('lit', c)
            i += 1

        # Check for quantifier after atom
        if i < len(pattern) and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            tokens.append((atom, quant))
        else:
            tokens.append((atom, None))

    return tokens


def _match(tokens, text, ti, si):
    if ti == len(tokens) and si == len(text):
        return True

    atom, quant = tokens[ti]

    if quant is None:
        # Must match exactly one character
        if si >= len(text):
            return False
        c = text[si]
        if _matches_atom(atom, c):
            return _match(tokens, text, ti + 1, si + 1)
        else:
            return False

    elif quant == '?':
        # Zero or one
        result = _match(tokens, text, ti + 1, si)
        if result:
            return True
        if si < len(text) and _matches_atom(atom, text[si]):
            return _match(tokens, text, ti + 1, si + 1)
        return False

    elif quant == '*':
        # Zero or more - try matching 0, 1, 2, ... characters
        for k in range(si, len(text) + 1):
            if k > si and not _matches_atom(atom, text[k - 1]):
                break
            if _match(tokens, text, ti + 1, k):
                return True
        return False

    elif quant == '+':
        # One or more - try matching 1, 2, ... characters
        for k in range(si + 1, len(text) + 1):
            if not _matches_atom(atom, text[k - 1]):
                break
            if _match(tokens, text, ti + 1, k):
                return True
        return False

    return False


def _matches_atom(atom, c):
    kind = atom[0]
    if kind == 'lit':
        return c == atom[1]
    elif kind == 'dot':
        return True
    elif kind == 'class':
        chars, negated = atom[1], atom[2]
        result = c in chars
        return not result if negated else result
    return False
