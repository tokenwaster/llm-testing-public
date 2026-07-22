def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)

    def backtrack(ti: int, si: int) -> bool:
        # ti: index into tokens, si: index into text
        if ti == len(tokens):
            return si == len(text)

        matcher, quant = tokens[ti]

        if quant == '':
            if si < len(text) and matcher(text[si]):
                return backtrack(ti + 1, si + 1)
            return False

        if quant == '?':
            # try one, then zero
            if si < len(text) and matcher(text[si]):
                if backtrack(ti + 1, si + 1):
                    return True
            return backtrack(ti + 1, si)

        if quant == '*':
            # greedy: consume as many as possible, then backtrack
            count = 0
            while si + count < len(text) and matcher(text[si + count]):
                count += 1
            for k in range(count, -1, -1):
                if backtrack(ti + 1, si + k):
                    return True
            return False

        if quant == '+':
            count = 0
            while si + count < len(text) and matcher(text[si + count]):
                count += 1
            for k in range(count, 0, -1):
                if backtrack(ti + 1, si + k):
                    return True
            return False

        raise ValueError(f"unknown quantifier {quant!r}")

    return backtrack(0, 0)


def _parse(pattern: str):
    """Parse a pattern into a list of (matcher, quantifier) tuples.

    matcher: callable char -> bool
    quantifier: one of '', '?', '*', '+'
    """
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c in '*+?':
            raise ValueError(f"quantifier {c!r} with nothing to repeat at index {i}")

        if c == '[':
            matcher, i = _parse_class(pattern, i)
        elif c == '.':
            matcher = lambda ch: True
            i += 1
        else:
            matcher = (lambda literal: (lambda ch: ch == literal))(c)
            i += 1

        # optional quantifier
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
    j = i + 1  # skip '['

    negate = False
    if j < n and pattern[j] == '^':
        negate = True
        j += 1

    # collect members: literal chars and ranges
    singles = set()
    ranges = []

    # A ']' immediately here would be an empty class; treat as malformed.
    first = True
    closed = False
    while j < n:
        ch = pattern[j]
        if ch == ']' and not first:
            closed = True
            j += 1
            break

        first = False

        # range: X-Y where Y is not ']'
        if (j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']'):
            lo = ch
            hi = pattern[j + 2]
            if ord(lo) > ord(hi):
                raise ValueError(f"invalid range {lo!r}-{hi!r} in class")
            ranges.append((ord(lo), ord(hi)))
            j += 3
        else:
            singles.add(ch)
            j += 1

    if not closed:
        raise ValueError("unclosed character class '['")

    if not singles and not ranges:
        raise ValueError("empty character class")

    def matcher(c, singles=singles, ranges=ranges, negate=negate):
        inside = c in singles or any(lo <= ord(c) <= hi for lo, hi in ranges)
        return inside != negate

    return matcher, j
