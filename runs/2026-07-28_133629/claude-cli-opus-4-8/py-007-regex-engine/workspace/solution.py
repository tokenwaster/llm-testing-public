def match(pattern: str, text: str) -> bool:
    """Report whether `pattern` matches the ENTIRE `text`.

    Supported regex subset:
      - literal characters
      - `.`            any single character
      - `*` `+` `?`    quantifiers on the preceding element
      - `[abc]` `[a-z0-9]` `[^abc]`  character classes (optionally quantified)
    """

    # --- Parse the pattern into a list of tokens -------------------------
    # Each token is (kind, data, quantifier) where:
    #   kind == 'char'  -> data is the literal character to match
    #   kind == 'any'   -> data is None (matches any single character)
    #   kind == 'class' -> data is a predicate(ch) -> bool
    # quantifier is one of '', '*', '+', '?'.
    tokens = _parse(pattern)

    # --- Recursive backtracking matcher ---------------------------------
    def matches(ti: int, si: int) -> bool:
        # ti: index into tokens, si: index into text.
        if ti == len(tokens):
            return si == len(text)

        kind, data, quant = tokens[ti]

        def single(pos: int) -> bool:
            # Does the token (ignoring its quantifier) match text[pos]?
            if pos >= len(text):
                return False
            if kind == 'char':
                return text[pos] == data
            if kind == 'any':
                return True
            # kind == 'class'
            return data(text[pos])

        if quant == '' :
            # Exactly one occurrence.
            if single(si):
                return matches(ti + 1, si + 1)
            return False

        if quant == '?':
            # Zero or one occurrence.
            if single(si) and matches(ti + 1, si + 1):
                return True
            return matches(ti + 1, si)

        if quant == '*':
            # Zero or more occurrences: try longest-first with backtracking.
            # Greedily consume as many as possible, then back off.
            count = 0
            while single(si + count):
                count += 1
            for n in range(count, -1, -1):
                if matches(ti + 1, si + n):
                    return True
            return False

        if quant == '+':
            # One or more occurrences.
            count = 0
            while single(si + count):
                count += 1
            for n in range(count, 0, -1):
                if matches(ti + 1, si + n):
                    return True
            return False

        raise ValueError("unknown quantifier: %r" % (quant,))

    return matches(0, 0)


def _parse(pattern: str):
    """Turn `pattern` into a list of (kind, data, quantifier) tokens.

    Raises ValueError on malformed patterns.
    """
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch == '*' or ch == '+' or ch == '?':
            # A quantifier with no preceding element is malformed.
            raise ValueError("quantifier %r has nothing to repeat" % (ch,))

        if ch == '.':
            token = ('any', None, '')
            i += 1

        elif ch == '[':
            predicate, i = _parse_class(pattern, i)
            token = ('class', predicate, '')

        else:
            # An ordinary literal character.
            token = ('char', ch, '')
            i += 1

        # Check for a following quantifier.
        if i < n and pattern[i] in '*+?':
            token = (token[0], token[1], pattern[i])
            i += 1

        tokens.append(token)

    return tokens


def _parse_class(pattern: str, start: int):
    """Parse a character class beginning at index `start` (a '[').

    Returns (predicate, next_index) where predicate(ch) -> bool.
    Raises ValueError if the class is unclosed.
    """
    n = len(pattern)
    i = start + 1  # skip '['

    negate = False
    if i < n and pattern[i] == '^':
        negate = True
        i += 1

    # Collect (single chars) and (ranges) until the closing ']'.
    singles = []
    ranges = []

    closed = False
    while i < n:
        ch = pattern[i]

        if ch == ']':
            closed = True
            i += 1
            break

        # Is this the start of a range like a-z?  Need a '-' followed by a
        # character that is not the closing ']'.
        if (i + 2 < n) and pattern[i + 1] == '-' and pattern[i + 2] != ']':
            ranges.append((ch, pattern[i + 2]))
            i += 3
        else:
            singles.append(ch)
            i += 1

    if not closed:
        raise ValueError("unclosed character class")

    singles_set = set(singles)

    def predicate(c: str) -> bool:
        inside = c in singles_set
        if not inside:
            for lo, hi in ranges:
                if lo <= c <= hi:
                    inside = True
                    break
        return inside != negate

    return predicate, i
