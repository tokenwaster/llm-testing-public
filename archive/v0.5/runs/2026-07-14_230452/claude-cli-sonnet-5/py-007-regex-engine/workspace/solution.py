def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)
    return _match_tokens(tokens, 0, text, 0)


def _parse(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            j = i + 1
            negate = False
            if j < n and pattern[j] == '^':
                negate = True
                j += 1
            class_start = j
            if j < n and pattern[j] == ']':
                j += 1
            while j < n and pattern[j] != ']':
                j += 1
            if j >= n or pattern[j] != ']':
                raise ValueError(f"Unclosed character class in pattern: {pattern}")
            class_body = pattern[class_start:j]
            if not class_body:
                raise ValueError(f"Empty character class in pattern: {pattern}")
            elem = ('class', negate, class_body)
            i = j + 1
        elif c == '.':
            elem = ('any',)
            i += 1
        elif c in '*+?':
            raise ValueError(f"Quantifier '{c}' with nothing to repeat in pattern: {pattern}")
        elif c == ']':
            raise ValueError(f"Unmatched ']' in pattern: {pattern}")
        else:
            elem = ('lit', c)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in '*+?':
                raise ValueError(f"Invalid consecutive quantifiers in pattern: {pattern}")

        tokens.append((elem, quant))
    return tokens


def _class_matches(class_body: str, negate: bool, ch: str) -> bool:
    i = 0
    n = len(class_body)
    matched = False
    while i < n:
        if i + 2 < n and class_body[i + 1] == '-':
            lo, hi = class_body[i], class_body[i + 2]
            if lo <= ch <= hi:
                matched = True
            i += 3
        else:
            if class_body[i] == ch:
                matched = True
            i += 1
    return matched != negate


def _elem_matches(elem, ch: str) -> bool:
    kind = elem[0]
    if kind == 'any':
        return True
    if kind == 'lit':
        return elem[1] == ch
    if kind == 'class':
        _, negate, class_body = elem
        return _class_matches(class_body, negate, ch)
    return False


def _match_tokens(tokens, ti: int, text: str, si: int) -> bool:
    if ti == len(tokens):
        return si == len(text)

    elem, quant = tokens[ti]

    if quant is None:
        if si < len(text) and _elem_matches(elem, text[si]):
            return _match_tokens(tokens, ti + 1, text, si + 1)
        return False

    if quant == '?':
        if si < len(text) and _elem_matches(elem, text[si]):
            if _match_tokens(tokens, ti + 1, text, si + 1):
                return True
        return _match_tokens(tokens, ti + 1, text, si)

    if quant == '*':
        count = 0
        while si + count < len(text) and _elem_matches(elem, text[si + count]):
            count += 1
        for k in range(count, -1, -1):
            if _match_tokens(tokens, ti + 1, text, si + k):
                return True
        return False

    if quant == '+':
        count = 0
        while si + count < len(text) and _elem_matches(elem, text[si + count]):
            count += 1
        for k in range(count, 0, -1):
            if _match_tokens(tokens, ti + 1, text, si + k):
                return True
        return False

    return False
