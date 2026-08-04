def match(pattern: str, text: str) -> bool:
    tokens = _parse(pattern)

    def backtrack(ti, si):
        if ti == len(tokens):
            return si == len(text)
        matcher, quant = tokens[ti]
        if quant == '*':
            # try as many as possible, backtrack
            # zero or more
            # greedy: try more first
            count = 0
            positions = [si]
            k = si
            while k < len(text) and matcher(text[k]):
                k += 1
                positions.append(k)
            for pos in reversed(positions):
                if backtrack(ti + 1, pos):
                    return True
            return False
        elif quant == '+':
            positions = []
            k = si
            while k < len(text) and matcher(text[k]):
                k += 1
                positions.append(k)
            for pos in reversed(positions):
                if backtrack(ti + 1, pos):
                    return True
            return False
        elif quant == '?':
            if si < len(text) and matcher(text[si]):
                if backtrack(ti + 1, si + 1):
                    return True
            return backtrack(ti + 1, si)
        else:
            if si < len(text) and matcher(text[si]):
                return backtrack(ti + 1, si + 1)
            return False

    return backtrack(0, 0)


def _parse(pattern):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '*' or c == '+' or c == '?':
            raise ValueError("quantifier with nothing before it")
        if c == '[':
            j = i + 1
            negate = False
            if j < n and pattern[j] == '^':
                negate = True
                j += 1
            chars = set()
            ranges = []
            found_close = False
            first = True
            while j < n:
                if pattern[j] == ']' and not first:
                    found_close = True
                    break
                # handle range
                if (j + 2 < n and pattern[j + 1] == '-' and
                        pattern[j + 2] != ']'):
                    ranges.append((pattern[j], pattern[j + 2]))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
                first = False
            if not found_close:
                raise ValueError("unclosed [")
            matcher = _make_class_matcher(chars, ranges, negate)
            i = j + 1
        elif c == '.':
            matcher = lambda ch: True
            i += 1
        else:
            matcher = (lambda literal: (lambda ch: ch == literal))(c)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        tokens.append((matcher, quant))
    return tokens


def _make_class_matcher(chars, ranges, negate):
    def matcher(ch):
        result = ch in chars
        if not result:
            for lo, hi in ranges:
                if lo <= ch <= hi:
                    result = True
                    break
        return (not result) if negate else result
    return matcher
