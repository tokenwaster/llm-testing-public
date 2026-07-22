def match(pattern: str, text: str) -> bool:
    # Parse the pattern into a list of (matcher, quantifier) tokens.
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]
        if c in '*+?':
            raise ValueError(f"Quantifier '{c}' has no preceding element")

        if c == '[':
            i += 1
            if i >= n:
                raise ValueError("Unclosed '['")

            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1

            ranges = []
            while i < n and pattern[i] != ']':
                start_char = pattern[i]
                i += 1
                if i < n and pattern[i] == '-' and i + 1 < n and pattern[i + 1] != ']':
                    i += 1  # skip '-'
                    end_char = pattern[i]
                    i += 1
                    if ord(start_char) > ord(end_char):
                        raise ValueError(f"Invalid range {start_char}-{end_char}")
                    ranges.append((start_char, end_char))
                else:
                    ranges.append((start_char, start_char))

            if i >= n:
                raise ValueError("Unclosed '['")
            i += 1  # skip ']'

            def make_class_matcher(ranges, negated):
                def matcher(ch):
                    in_range = any(s <= ch <= e for s, e in ranges)
                    return in_range != negated
                return matcher

            matcher = make_class_matcher(ranges, negated)

            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            else:
                quant = None
            tokens.append((matcher, quant))
        else:
            if c == '.':
                matcher = lambda ch: True
            else:
                matcher = lambda ch, c=c: ch == c
            i += 1
            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            else:
                quant = None
            tokens.append((matcher, quant))

    text_len = len(text)
    memo = {}

    def match_from(ti: int, si: int) -> bool:
        if ti == len(tokens):
            return si == text_len
        key = (ti, si)
        if key in memo:
            return memo[key]

        matcher, quant = tokens[ti]
        if quant is None:
            if si < text_len and matcher(text[si]):
                res = match_from(ti + 1, si + 1)
            else:
                res = False
        elif quant == '?':
            res = False
            if si < text_len and matcher(text[si]):
                if match_from(ti + 1, si + 1):
                    res = True
            if not res:
                res = match_from(ti + 1, si)
        elif quant == '*':
            res = match_from(ti + 1, si)  # zero occurrences
            if not res and si < text_len and matcher(text[si]):
                res = match_from(ti, si + 1)  # one or more
        elif quant == '+':
            if si < text_len and matcher(text[si]):
                res = match_from(ti + 1, si + 1) or match_from(ti, si + 1)
            else:
                res = False
        else:
            res = False

        memo[key] = res
        return res

    return match_from(0, 0)
