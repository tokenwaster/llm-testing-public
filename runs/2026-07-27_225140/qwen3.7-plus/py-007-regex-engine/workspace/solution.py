def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match_here(tokens, 0, text, 0)


def _parse(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in '*+?':
            raise ValueError(f"Quantifier '{c}' without preceding element")

        # Build matcher function for this unit
        if c == '.':
            matcher = lambda ch: True
            i += 1
        elif c == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            chars = set()
            while j < n and pattern[j] != ']':
                # Check for range like a-z
                if (j + 2 < n and pattern[j + 1] == '-'
                        and pattern[j + 2] != ']'):
                    lo, hi = ord(pattern[j]), ord(pattern[j + 2])
                    for code in range(lo, hi + 1):
                        chars.add(chr(code))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= n:
                raise ValueError("Unclosed character class '['")
            if not chars:
                raise ValueError("Empty character class '[]'")
            i = j + 1  # skip past ']'
            if negated:
                _chars = frozenset(chars)
                matcher = lambda ch, _c=_chars: ch not in _c
            else:
                _chars = frozenset(chars)
                matcher = lambda ch, _c=_chars: ch in _c
        else:
            _c = c
            matcher = lambda ch, _ch=_c: ch == _ch
            i += 1

        # Check for quantifier
        quantifier = None
        if i < n and pattern[i] in '*+?':
            quantifier = pattern[i]
            i += 1

        tokens.append((matcher, quantifier))

    return tokens


def _match_here(tokens, ti, text, si):
    # If we've consumed all tokens, we must have consumed all text
    if ti == len(tokens):
        return si == len(text)

    matcher, quantifier = tokens[ti]

    if quantifier == '*':
        # Greedy: find max possible matches, then try from max down to 0
        count = 0
        while si + count < len(text) and matcher(text[si + count]):
            count += 1
        for k in range(count, -1, -1):
            if _match_here(tokens, ti + 1, text, si + k):
                return True
        return False

    elif quantifier == '+':
        # Greedy: find max possible matches, must match at least 1
        count = 0
        while si + count < len(text) and matcher(text[si + count]):
            count += 1
        if count == 0:
            return False
        for k in range(count, 0, -1):
            if _match_here(tokens, ti + 1, text, si + k):
                return True
        return False

    elif quantifier == '?':
        # Greedy: try matching 1 first, then 0
        if si < len(text) and matcher(text[si]):
            if _match_here(tokens, ti + 1, text, si + 1):
                return True
        return _match_here(tokens, ti + 1, text, si)

    else:
        # No quantifier: must match exactly one character
        if si < len(text) and matcher(text[si]):
            return _match_here(tokens, ti + 1, text, si + 1)
        return False
