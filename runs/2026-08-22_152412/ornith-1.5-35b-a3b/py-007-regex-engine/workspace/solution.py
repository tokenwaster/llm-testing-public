def match(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the ENTIRE `text`.

    Supported subset: literals, '.', '*', '+', '?', and character classes
    ([abc], [a-z0-9], [^...]). Raises ValueError on malformed patterns.
    """
    tokens = _parse(pattern)

    def rec(ti: int, pi: int) -> bool:
        # Match tokens[ti:] against text[pi:] entirely.
        if ti == len(tokens):
            return pi == len(text)

        element, q = tokens[ti]

        if q == 'one':
            if pi < len(text) and _matches(element, text[pi]):
                return rec(ti + 1, pi + 1)
            return False

        if q == '?':
            # zero occurrences
            if rec(ti + 1, pi):
                return True
            # one occurrence
            if pi < len(text) and _matches(element, text[pi]):
                return rec(ti + 1, pi + 1)
            return False

        if q == '*':
            # zero occurrences
            if rec(ti + 1, pi):
                return True
            # one or more: consume a matching char and retry same token
            if pi < len(text) and _matches(element, text[pi]):
                return rec(ti, pi + 1)
            return False

        # q == '+': must match at least once, then behaves like '*'
        if pi < len(text) and _matches(element, text[pi]):
            return rec(ti, pi + 1)
        return False

    return rec(0, 0)


def _matches(element, ch: str) -> bool:
    """Does a single character `ch` satisfy the given element?"""
    kind = element[0]
    if kind == 'dot':
        return True
    if kind == 'lit':
        return element[1] == ch
    # class: ('class', negated, ranges)
    negated, ranges = element[1], element[2]
    o = ord(ch)
    matched = any(start <= o <= end for start, end in ranges)
    return matched != negated


def _parse_class(pattern: str, i: int):
    """Parse a character class starting at pattern[i] == '['.

    Returns (element_tuple, next_index). element_tuple is
    ('class', negated, ranges) where ranges is a list of inclusive
    (start, end) ordinal tuples.
    """
    negated = False
    j = i + 1
    if j < len(pattern) and pattern[j] == '^':
        negated = True
        j += 1

    ranges = []
    while j < len(pattern) and pattern[j] != ']':
        c = pattern[j]
        # Detect a range like 'a-z' (end char must not be the closing ']')
        if (j + 2 < len(pattern)
                and pattern[j + 1] == '-'
                and pattern[j + 2] != ']'):
            ranges.append((ord(c), ord(pattern[j + 2])))
            j += 3
        else:
            ranges.append((ord(c), ord(c)))
            j += 1

    if j >= len(pattern):
        raise ValueError("Unclosed character class in pattern")
    if not ranges:
        raise ValueError("Empty character class in pattern")

    return ('class', negated, ranges), j + 1


def _parse(pattern: str):
    """Turn the pattern string into a list of (element, quantifier) tokens."""
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        # A quantifier with nothing before it is malformed. This also catches
        # consecutive quantifiers (e.g. "a**") since we only reach here after
        # consuming a full element + its optional quantifier.
        if c in '*+?':
            raise ValueError("Quantifier '%s' with nothing before it" % c)

        if c == '[':
            element, i = _parse_class(pattern, i)
        elif c == '.':
            element = ('dot', None)
            i += 1
        else:
            element = ('lit', c)
            i += 1

        # Optional quantifier following the element.
        if i < n and pattern[i] in '*+?':
            q = pattern[i]
            i += 1
        else:
            q = 'one'

        tokens.append((element, q))

    return tokens
