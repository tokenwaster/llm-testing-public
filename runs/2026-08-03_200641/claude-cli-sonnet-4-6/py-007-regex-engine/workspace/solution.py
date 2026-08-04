def match(pattern: str, text: str) -> bool:
    _validate(pattern)
    return _do_match(pattern, 0, text, 0)


def _validate(pattern: str) -> None:
    pi = 0
    prev_element = False
    while pi < len(pattern):
        ch = pattern[pi]
        if ch == '[':
            _, pi = _parse_class(pattern, pi)
            prev_element = True
        elif ch in ('*', '+', '?'):
            if not prev_element:
                raise ValueError(f"Quantifier '{ch}' has no preceding element")
            pi += 1
            prev_element = False
        elif ch == ']':
            raise ValueError("Unexpected ']' in pattern")
        else:
            pi += 1
            prev_element = True


def _parse_class(pattern: str, pi: int):
    """Parse [...] starting at pi. Return (predicate, next_pi)."""
    if pi >= len(pattern) or pattern[pi] != '[':
        raise ValueError("Expected '['")
    pi += 1

    negate = False
    if pi < len(pattern) and pattern[pi] == '^':
        negate = True
        pi += 1

    chars = []
    ranges = []

    while True:
        if pi >= len(pattern):
            raise ValueError("Unclosed '[' in pattern")
        if pattern[pi] == ']':
            break
        # Range: x-y where y is not ']'
        if (pi + 2 < len(pattern)
                and pattern[pi + 1] == '-'
                and pattern[pi + 2] != ']'):
            ranges.append((pattern[pi], pattern[pi + 2]))
            pi += 3
        else:
            chars.append(pattern[pi])
            pi += 1

    pi += 1  # skip ']'
    char_set = frozenset(chars)

    def predicate(c, _cs=char_set, _rs=ranges, _neg=negate):
        hit = c in _cs or any(lo <= c <= hi for lo, hi in _rs)
        return (not hit) if _neg else hit

    return predicate, pi


def _parse_element(pattern: str, pi: int):
    """Parse one element at pi. Return (predicate, next_pi)."""
    ch = pattern[pi]
    if ch == '[':
        return _parse_class(pattern, pi)
    if ch == '.':
        return (lambda c: True), pi + 1
    return (lambda c, lit=ch: c == lit), pi + 1


def _do_match(pattern: str, pi: int, text: str, ti: int) -> bool:
    if pi == len(pattern):
        return ti == len(text)

    elem_pred, next_pi = _parse_element(pattern, pi)

    quantifier = None
    rest_pi = next_pi
    if next_pi < len(pattern) and pattern[next_pi] in ('*', '+', '?'):
        quantifier = pattern[next_pi]
        rest_pi = next_pi + 1

    if quantifier is None:
        if ti < len(text) and elem_pred(text[ti]):
            return _do_match(pattern, next_pi, text, ti + 1)
        return False

    if quantifier == '?':
        if ti < len(text) and elem_pred(text[ti]):
            if _do_match(pattern, rest_pi, text, ti + 1):
                return True
        return _do_match(pattern, rest_pi, text, ti)

    if quantifier == '*':
        # Greedy: find max match length, then backtrack
        max_ti = ti
        while max_ti < len(text) and elem_pred(text[max_ti]):
            max_ti += 1
        for j in range(max_ti, ti - 1, -1):
            if _do_match(pattern, rest_pi, text, j):
                return True
        return False

    if quantifier == '+':
        # Must match at least one
        if ti >= len(text) or not elem_pred(text[ti]):
            return False
        start = ti + 1
        max_ti = start
        while max_ti < len(text) and elem_pred(text[max_ti]):
            max_ti += 1
        for j in range(max_ti, start - 1, -1):
            if _do_match(pattern, rest_pi, text, j):
                return True
        return False

    return False  # unreachable after validation
