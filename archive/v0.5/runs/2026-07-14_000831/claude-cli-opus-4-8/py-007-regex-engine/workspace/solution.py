def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)

    def backtrack(ti: int, si: int) -> bool:
        if ti == len(tokens):
            return si == len(text)

        matcher, quant = tokens[ti]

        if quant == '':
            if si < len(text) and matcher(text[si]):
                return backtrack(ti + 1, si + 1)
            return False

        if quant == '?':
            if si < len(text) and matcher(text[si]) and backtrack(ti + 1, si + 1):
                return True
            return backtrack(ti + 1, si)

        if quant == '*':
            # try to consume as many as possible, backtracking down to zero
            count = 0
            while si + count < len(text) and matcher(text[si + count]):
                count += 1
            for n in range(count, -1, -1):
                if backtrack(ti + 1, si + n):
                    return True
            return False

        if quant == '+':
            count = 0
            while si + count < len(text) and matcher(text[si + count]):
                count += 1
            for n in range(count, 0, -1):
                if backtrack(ti + 1, si + n):
                    return True
            return False

        raise ValueError(f"unknown quantifier: {quant!r}")

    return backtrack(0, 0)


def _parse(pattern: str):
    """Parse a pattern into a list of (matcher, quantifier) tuples.

    matcher: callable taking a single character, returning bool.
    quantifier: one of '', '?', '*', '+'.
    """
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c in '*+?':
            raise ValueError(f"quantifier '{c}' with nothing before it")

        if c == '[':
            matcher, i = _parse_class(pattern, i)
        elif c == '.':
            matcher = lambda ch: True
            i += 1
        else:
            matcher = (lambda expected: lambda ch: ch == expected)(c)
            i += 1

        quant = ''
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append((matcher, quant))

    return tokens


def _parse_class(pattern: str, i: int):
    """Parse a character class starting at pattern[i] == '['.

    Returns (matcher, next_index).
    """
    n = len(pattern)
    i += 1  # skip '['

    negate = False
    if i < n and pattern[i] == '^':
        negate = True
        i += 1

    members = []  # list of ('char', c) or ('range', lo, hi)
    got_any = False

    while i < n and pattern[i] != ']':
        lo = pattern[i]
        i += 1

        # range: a-z, but a trailing '-' before ']' is a literal '-'
        if i + 1 < n and pattern[i] == '-' and pattern[i + 1] != ']':
            hi = pattern[i + 1]
            if ord(lo) > ord(hi):
                raise ValueError(f"invalid range: {lo}-{hi}")
            members.append(('range', lo, hi))
            i += 2
        else:
            members.append(('char', lo))
        got_any = True

    if i >= n:
        raise ValueError("unclosed '['")

    # pattern[i] == ']'
    i += 1  # skip ']'

    if not got_any:
        raise ValueError("empty character class")

    def matcher(ch, members=members, negate=negate):
        matched = False
        for m in members:
            if m[0] == 'char':
                if ch == m[1]:
                    matched = True
                    break
            else:
                if m[1] <= ch <= m[2]:
                    matched = True
                    break
        return matched != negate

    return matcher, i
