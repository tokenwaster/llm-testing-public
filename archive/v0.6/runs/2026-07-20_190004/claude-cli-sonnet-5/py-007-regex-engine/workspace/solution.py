def _parse_class_body(body):
    chars = set()
    i = 0
    n = len(body)
    while i < n:
        if i + 2 < n and body[i + 1] == '-':
            a, b = body[i], body[i + 2]
            if ord(a) > ord(b):
                raise ValueError("Bad range in character class: %r-%r" % (a, b))
            for code in range(ord(a), ord(b) + 1):
                chars.add(chr(code))
            i += 3
        else:
            chars.add(body[i])
            i += 1
    return chars


def _parse(pattern):
    elements = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            close = pattern.find(']', i + 1)
            if close == -1:
                raise ValueError("Unclosed character class starting at index %d" % i)
            body = pattern[i + 1:close]
            negate = False
            if body.startswith('^'):
                negate = True
                body = body[1:]
            if body == '':
                raise ValueError("Empty character class")
            chars = _parse_class_body(body)
            matcher = ('class', chars, negate)
            i = close + 1
        elif c == '.':
            matcher = ('any',)
            i += 1
        elif c in '*+?':
            raise ValueError("Quantifier %r with nothing to repeat" % c)
        else:
            matcher = ('lit', c)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        elements.append((matcher, quant))
    return elements


def _matches_atom(matcher, ch):
    kind = matcher[0]
    if kind == 'any':
        return True
    if kind == 'lit':
        return matcher[1] == ch
    # kind == 'class'
    _, chars, negate = matcher
    in_set = ch in chars
    return (not in_set) if negate else in_set


def _match_star(elements, ei, text, ti, matcher):
    # Zero-or-more of `matcher` starting at text[ti], then continue matching
    # the rest of `elements` from index ei + 1.
    if _match_elements(elements, ei + 1, text, ti):
        return True
    if ti < len(text) and _matches_atom(matcher, text[ti]):
        return _match_star(elements, ei, text, ti + 1, matcher)
    return False


def _match_elements(elements, ei, text, ti):
    if ei == len(elements):
        return ti == len(text)

    matcher, quant = elements[ei]

    if quant is None:
        if ti < len(text) and _matches_atom(matcher, text[ti]):
            return _match_elements(elements, ei + 1, text, ti + 1)
        return False

    if quant == '?':
        if ti < len(text) and _matches_atom(matcher, text[ti]):
            if _match_elements(elements, ei + 1, text, ti + 1):
                return True
        return _match_elements(elements, ei + 1, text, ti)

    if quant == '*':
        return _match_star(elements, ei, text, ti, matcher)

    if quant == '+':
        if ti < len(text) and _matches_atom(matcher, text[ti]):
            return _match_star(elements, ei, text, ti + 1, matcher)
        return False

    raise ValueError("Unknown quantifier %r" % quant)


def match(pattern: str, text: str) -> bool:
    elements = _parse(pattern)
    return _match_elements(elements, 0, text, 0)
