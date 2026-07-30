def match(pattern: str, text: str) -> bool:
    # Parse pattern into tokens
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            # parse character class
            j = i + 1
            if j >= n:
                raise ValueError("Unclosed character class")
            neg = False
            if pattern[j] == '^':
                neg = True
                j += 1
            if j >= n:
                raise ValueError("Unclosed character class")
            chars = set()
            ranges = []
            while j < n and pattern[j] != ']':
                if j + 2 < n and pattern[j+1] == '-' and pattern[j+2] != ']':
                    start = pattern[j]
                    end = pattern[j+2]
                    if start > end:
                        raise ValueError("Invalid range in character class")
                    ranges.append((start, end))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= n:
                raise ValueError("Unclosed character class")
            # j is at ']'
            i = j + 1
            # check for quantifier
            quant = None
            if i < n and pattern[i] in ('*', '+', '?'):
                quant = pattern[i]
                i += 1
            tokens.append(('class', (neg, chars, ranges), quant))
        elif c in ('*', '+', '?'):
            if not tokens:
                raise ValueError("Quantifier with no preceding element")
            # attach quantifier to previous token if not already present
            if tokens[-1][2] is not None:
                raise ValueError("Multiple quantifiers on same element")
            prev = tokens[-1]
            tokens[-1] = (prev[0], prev[1], c)
            i += 1
        elif c == '.':
            quant = None
            if i + 1 < n and pattern[i+1] in ('*', '+', '?'):
                quant = pattern[i+1]
                i += 2
            else:
                i += 1
            tokens.append(('dot', None, quant))
        else:
            quant = None
            if i + 1 < n and pattern[i+1] in ('*', '+', '?'):
                quant = pattern[i+1]
                i += 2
            else:
                i += 1
            tokens.append(('lit', c, quant))

    # Validate tokens: no quantifier without preceding element already handled
    # Empty pattern
    if not tokens:
        return text == ""

    def matches_class(ch, cls):
        neg, chars, ranges = cls
        if ch in chars:
            matched = True
        else:
            matched = False
            for s, e in ranges:
                if s <= ch <= e:
                    matched = True
                    break
        return (not matched) if neg else matched

    def match_token(tok, ch):
        typ, val, _ = tok
        if typ == 'lit':
            return ch == val
        elif typ == 'dot':
            return True
        elif typ == 'class':
            return matches_class(ch, val)
        return False

    # Recursive backtracking matcher over tokens and text index
    def backtrack(ti, si):
        # ti: token index, si: text index
        if ti == len(tokens):
            return si == len(text)
        typ, val, quant = tokens[ti]
        if quant is None:
            if si >= len(text):
                return False
            if match_token(tokens[ti], text[si]):
                return backtrack(ti + 1, si + 1)
            return False
        elif quant == '?':
            # try zero
            if backtrack(ti + 1, si):
                return True
            # try one
            if si < len(text) and match_token(tokens[ti], text[si]):
                return backtrack(ti + 1, si + 1)
            return False
        elif quant == '*':
            # try zero
            if backtrack(ti + 1, si):
                return True
            # try one or more
            if si < len(text) and match_token(tokens[ti], text[si]):
                return backtrack(ti, si + 1)
            return False
        elif quant == '+':
            # must match at least one
            if si >= len(text) or not match_token(tokens[ti], text[si]):
                return False
            # try one then maybe more
            if backtrack(ti + 1, si + 1):
                return True
            return backtrack(ti, si + 1)
        return False

    return backtrack(0, 0)
