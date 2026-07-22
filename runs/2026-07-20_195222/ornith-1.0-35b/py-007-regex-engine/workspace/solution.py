def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)
    return _match(tokens, 0, text, 0)


def _parse_pattern(pattern):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c in '*+?':
            raise ValueError(f"modifier '{c}' without preceding element at position {i}")

        if c == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1

            elements = []
            while j < n and pattern[j] != ']':
                elem_c = pattern[j]
                # check for range: x-y where y != ']'
                if j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']':
                    elements.append((elem_c, pattern[j + 2]))
                    j += 3
                else:
                    elements.append(elem_c)
                    j += 1

            if j >= n:
                raise ValueError("unclosed '[' in pattern")

            tokens.append(('class', negated, elements, None))
            i = j + 1

        elif c == '.':
            tokens.append(('dot', None))
            i += 1

        else:
            tokens.append(('lit', c, None))
            i += 1

        # check for quantifier following this element
        if i < n and pattern[i] in '*+?':
            old = tokens[-1]
            tokens[-1] = old[:-1] + (pattern[i],)
            i += 1

    return tokens


def _match(tokens, tidx, text, sidx):
    if tidx == len(tokens):
        return sidx == len(text)

    token = tokens[tidx]
    ttype = token[0]

    if ttype == 'lit':
        char, quantifier = token[1], token[2]
    elif ttype == 'dot':
        quantifier = token[1]
    elif ttype == 'class':
        negated, elements, quantifier = token[1], token[2], token[3]
    else:
        raise ValueError(f"unknown token type: {ttype}")

    if quantifier is None:
        # must match exactly once
        if sidx < len(text) and _matches_char(token, text[sidx]):
            return _match(tokens, tidx + 1, text, sidx + 1)
        return False

    elif quantifier == '?':
        # try zero matches first, then one match
        if _match(tokens, tidx + 1, text, sidx):
            return True
        if sidx < len(text) and _matches_char(token, text[sidx]):
            if _match(tokens, tidx + 1, text, sidx + 1):
                return True
        return False

    elif quantifier == '*':
        # try matching 0, 1, 2, ... occurrences
        k = 0
        while True:
            if _match(tokens, tidx + 1, text, sidx + k):
                return True
            if sidx + k >= len(text) or not _matches_char(token, text[sidx + k]):
                break
            k += 1
        return False

    elif quantifier == '+':
        # must match at least once; try matching 1, 2, 3, ... occurrences
        k = 1
        while True:
            if _match(tokens, tidx + 1, text, sidx + k):
                return True
            if sidx + k >= len(text) or not _matches_char(token, text[sidx + k]):
                break
            k += 1
        return False

    raise ValueError(f"unknown quantifier: {quantifier}")


def _matches_char(token, ch):
    ttype = token[0]
    if ttype == 'lit':
        return ch == token[1]
    elif ttype == 'dot':
        return True
    elif ttype == 'class':
        negated = token[1]
        elements = token[2]
        matched = False
        for elem in elements:
            if isinstance(elem, tuple):
                # range (start, end)
                if elem[0] <= ch <= elem[1]:
                    matched = True
                    break
            else:
                if ch == elem:
                    matched = True
                    break
        return (not matched) if negated else matched
    raise ValueError(f"unknown token type: {ttype}")
