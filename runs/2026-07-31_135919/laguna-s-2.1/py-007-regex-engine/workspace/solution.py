def match(pattern: str, text: str) -> bool:
    elements = _parse_pattern(pattern)
    memo = {}
    return _match_elements(elements, text, 0, 0, memo)


def _parse_pattern(pattern):
    """Parse a regex pattern into a list of (element, quantifier) tuples."""
    elements = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            chars = set()
            while j < n and pattern[j] != ']':
                if (j + 1 < n and pattern[j + 1] == '-' and
                        j + 2 < n and pattern[j + 2] != ']'):
                    start = pattern[j]
                    end = pattern[j + 2]
                    if start > end:
                        raise ValueError("invalid character range")
                    for code in range(ord(start), ord(end) + 1):
                        chars.add(chr(code))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= n:
                raise ValueError("unclosed character class")
            element = ('class', negated, frozenset(chars))
            i = j + 1
        elif c == '.':
            element = ('dot',)
            i += 1
        elif c in '*+?':
            raise ValueError("quantifier without preceding element")
        else:
            element = ('char', c)
            i += 1

        if i < n and pattern[i] in '*+?':
            quantifier = pattern[i]
            i += 1
        else:
            quantifier = None

        elements.append((element, quantifier))

    return elements


def _matches_element(element, char):
    """Check if a single element matches a single character."""
    kind = element[0]
    if kind == 'char':
        return char == element[1]
    elif kind == 'dot':
        return True
    elif kind == 'class':
        negated = element[1]
        chars = element[2]
        if negated:
            return char not in chars
        else:
            return char in chars
    return False


def _match_elements(elements, text, idx, pos, memo):
    """Recursively match elements against text using backtracking."""
    if idx >= len(elements):
        return pos >= len(text)

    key = (idx, pos)
    if key in memo:
        return memo[key]

    element, quantifier = elements[idx]

    if quantifier is None:
        if pos >= len(text):
            result = False
        else:
            result = (_matches_element(element, text[pos]) and
                      _match_elements(elements, text, idx + 1, pos + 1, memo))
    elif quantifier == '*':
        result = _match_elements(elements, text, idx + 1, pos, memo)
        if not result:
            k = pos
            while k < len(text) and _matches_element(element, text[k]):
                k += 1
                if _match_elements(elements, text, idx + 1, k, memo):
                    result = True
                    break
    elif quantifier == '+':
        if pos >= len(text) or not _matches_element(element, text[pos]):
            result = False
        else:
            result = _match_elements(elements, text, idx + 1, pos + 1, memo)
            k = pos + 1
            while not result and k < len(text) and _matches_element(element, text[k]):
                k += 1
                result = _match_elements(elements, text, idx + 1, k, memo)
    elif quantifier == '?':
        result = _match_elements(elements, text, idx + 1, pos, memo)
        if not result and pos < len(text) and _matches_element(element, text[pos]):
            result = _match_elements(elements, text, idx + 1, pos + 1, memo)

    memo[key] = result
    return result
