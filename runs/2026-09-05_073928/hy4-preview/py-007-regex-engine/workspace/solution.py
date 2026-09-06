from functools import lru_cache


def _parse_character_class(pattern: str, i: int):
    """Parse a character class starting at pattern[i] == '['.

    Returns (predicate, next_index).
    """
    n = len(pattern)
    i += 1  # skip '['

    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1

    ranges = []

    # A ']' immediately after '[' or '[^' is treated as a literal ']'.
    if i < n and pattern[i] == "]":
        ranges.append(("]", "]"))
        i += 1

    while i < n and pattern[i] != "]":
        start = pattern[i]
        i += 1

        if i + 1 < n and pattern[i] == "-" and pattern[i + 1] != "]":
            end = pattern[i + 1]
            if start > end:
                raise ValueError(f"invalid character range: {start!r}-{end!r}")
            ranges.append((start, end))
            i += 2
        else:
            ranges.append((start, start))

    if i >= n or pattern[i] != "]":
        raise ValueError("unclosed character class")
    if not ranges:
        raise ValueError("empty character class")

    def predicate(ch: str) -> bool:
        found = any(start <= ch <= end for start, end in ranges)
        return not found if negated else found

    return predicate, i + 1


def _parse_pattern(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError(f"quantifier {ch!r} with nothing to repeat")

        if ch == ".":
            predicate = lambda _: True
            i += 1
        elif ch == "[":
            predicate, i = _parse_character_class(pattern, i)
        else:
            predicate = (lambda c, lit=ch: c == lit)
            i += 1

        min_rep = 1
        max_rep = 1

        if i < n and pattern[i] in "*+?":
            q = pattern[i]
            if q == "*":
                min_rep, max_rep = 0, None
            elif q == "+":
                min_rep, max_rep = 1, None
            else:  # '?'
                min_rep, max_rep = 0, 1
            i += 1

        tokens.append((predicate, min_rep, max_rep))

    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)
    n = len(text)

    @lru_cache(maxsize=None)
    def match_tokens(ti: int, si: int) -> bool:
        if ti == len(tokens):
            return si == n

        predicate, min_rep, max_rep = tokens[ti]

        pos = si
        for _ in range(min_rep):
            if pos >= n or not predicate(text[pos]):
                return False
            pos += 1

        stops = []
        count = min_rep
        while True:
            stops.append(pos)
            if max_rep is not None and count >= max_rep:
                break
            if pos >= n or not predicate(text[pos]):
                break
            pos += 1
            count += 1

        for stop in reversed(stops):
            if match_tokens(ti + 1, stop):
                return True
        return False

    return match_tokens(0, 0)
