def _parse(pattern):
    """Parse pattern into a list of (matcher, quantifier) tokens.

    matcher: function(char) -> bool
    quantifier: '' | '*' | '+' | '?'
    """
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]

        if c in '*+?':
            raise ValueError(
                "quantifier '%s' at position %d has no preceding element" % (c, i)
            )

        if c == '[':
            j = i + 1
            negate = False
            if j < n and pattern[j] == '^':
                negate = True
                j += 1

            items = []
            class_body_start = j
            while j < n and pattern[j] != ']':
                if j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']':
                    lo, hi = pattern[j], pattern[j + 2]
                    if lo > hi:
                        raise ValueError("invalid range '%s-%s' in character class" % (lo, hi))
                    items.append((lo, hi))
                    j += 3
                else:
                    items.append((pattern[j], pattern[j]))
                    j += 1

            if j >= n:
                raise ValueError("unclosed character class starting at position %d" % i)
            if j == class_body_start:
                raise ValueError("empty character class at position %d" % i)

            def matcher(ch, items=items, negate=negate):
                inside = any(lo <= ch <= hi for lo, hi in items)
                return inside != negate

            i = j + 1  # position right after ']'
        elif c == '.':
            def matcher(ch):
                return True
            i += 1
        else:
            def matcher(ch, c=c):
                return ch == c
            i += 1

        quant = ''
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append((matcher, quant))

    return tokens


def _match_tokens(tokens, ti, text, si):
    if ti == len(tokens):
        return si == len(text)

    matcher, quant = tokens[ti]

    if quant == '':
        if si < len(text) and matcher(text[si]):
            return _match_tokens(tokens, ti + 1, text, si + 1)
        return False

    if quant == '?':
        if si < len(text) and matcher(text[si]) and _match_tokens(tokens, ti + 1, text, si + 1):
            return True
        return _match_tokens(tokens, ti + 1, text, si)

    if quant == '*':
        j = si
        while j < len(text) and matcher(text[j]):
            j += 1
        while j >= si:
            if _match_tokens(tokens, ti + 1, text, j):
                return True
            j -= 1
        return False

    if quant == '+':
        if si >= len(text) or not matcher(text[si]):
            return False
        j = si + 1
        while j < len(text) and matcher(text[j]):
            j += 1
        while j >= si + 1:
            if _match_tokens(tokens, ti + 1, text, j):
                return True
            j -= 1
        return False

    raise ValueError("unknown quantifier: %r" % quant)


def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match_tokens(tokens, 0, text, 0)
