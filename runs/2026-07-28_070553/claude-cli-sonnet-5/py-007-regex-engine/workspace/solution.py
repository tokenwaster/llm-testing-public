import string


def _parse_class(pattern, i):
    """Parse a character class starting at pattern[i] == '['.
    Returns (matcher, next_index) where matcher(ch) -> bool.
    """
    n = len(pattern)
    j = i + 1
    if j >= n:
        raise ValueError("Unclosed character class")

    negate = False
    if j < n and pattern[j] == '^':
        negate = True
        j += 1

    members = set()
    ranges = []
    seen_any = False

    # ']' right after '[' or '[^' is treated as a literal in classic regex,
    # but we won't special-case it; require an explicit closing bracket.
    while True:
        if j >= n:
            raise ValueError("Unclosed character class")
        ch = pattern[j]
        if ch == ']':
            if not seen_any:
                raise ValueError("Empty character class")
            break
        if ch == '\\':
            j += 1
            if j >= n:
                raise ValueError("Dangling escape in character class")
            lit = pattern[j]
            # check for range
            if j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']':
                start = lit
                end = pattern[j + 2]
                if start > end:
                    raise ValueError("Invalid range in character class")
                ranges.append((start, end))
                j += 3
            else:
                members.add(lit)
                j += 1
            seen_any = True
            continue

        # check for a range like a-z
        if j + 2 < n and pattern[j + 1] == '-' and pattern[j + 2] != ']':
            start = ch
            end = pattern[j + 2]
            if start > end:
                raise ValueError("Invalid range in character class")
            ranges.append((start, end))
            j += 3
        else:
            members.add(ch)
            j += 1
        seen_any = True

    end_index = j + 1  # index just past ']'

    def matcher(c):
        result = (c in members) or any(start <= c <= end for start, end in ranges)
        return (not result) if negate else result

    return matcher, end_index


def _parse_pattern(pattern):
    """Parse pattern into a list of elements, each a matcher function.
    Returns list of matcher callables (each matches exactly one character).
    """
    elements = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch == '[':
            matcher, i = _parse_class(pattern, i)
            elements.append(matcher)
        elif ch == '.':
            elements.append(lambda c: True)
            i += 1
        elif ch == '\\':
            i += 1
            if i >= n:
                raise ValueError("Dangling escape at end of pattern")
            lit = pattern[i]
            elements.append((lambda lit: lambda c: c == lit)(lit))
            i += 1
        elif ch in '*+?':
            raise ValueError(f"Quantifier '{ch}' with nothing to repeat")
        elif ch == ']':
            raise ValueError("Unmatched ']' in pattern")
        else:
            elements.append((lambda ch: lambda c: c == ch)(ch))
            i += 1
    return elements


def _tokenize(pattern):
    """Tokenize pattern into (matcher, quantifier) pairs.
    quantifier is one of None, '*', '+', '?'.
    """
    n = len(pattern)
    tokens = []
    i = 0
    while i < n:
        ch = pattern[i]
        if ch == '[':
            matcher, i = _parse_class(pattern, i)
        elif ch == '.':
            matcher = lambda c: True
            i += 1
        elif ch == '\\':
            i += 1
            if i >= n:
                raise ValueError("Dangling escape at end of pattern")
            lit = pattern[i]
            matcher = (lambda lit: lambda c: c == lit)(lit)
            i += 1
        elif ch in '*+?':
            raise ValueError(f"Quantifier '{ch}' with nothing to repeat")
        elif ch == ']':
            raise ValueError("Unmatched ']' in pattern")
        else:
            matcher = (lambda ch: lambda c: c == ch)(ch)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in '*+?':
                raise ValueError("Consecutive quantifiers not allowed")

        tokens.append((matcher, quant))

    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = _tokenize(pattern)

    memo = {}

    def rec(ti, si):
        key = (ti, si)
        if key in memo:
            return memo[key]

        if ti == len(tokens):
            result = si == len(text)
            memo[key] = result
            return result

        matcher, quant = tokens[ti]

        def matches_here():
            return si < len(text) and matcher(text[si])

        if quant is None:
            result = matches_here() and rec(ti + 1, si + 1)
        elif quant == '?':
            result = (matches_here() and rec(ti + 1, si + 1)) or rec(ti + 1, si)
        elif quant == '*':
            result = rec(ti + 1, si)
            if not result and matches_here():
                result = rec(ti, si + 1)
        elif quant == '+':
            result = matches_here() and (rec(ti + 1, si + 1) or rec(ti, si + 1))
        else:
            raise ValueError(f"Unknown quantifier: {quant}")

        memo[key] = result
        return result

    return rec(0, 0)
