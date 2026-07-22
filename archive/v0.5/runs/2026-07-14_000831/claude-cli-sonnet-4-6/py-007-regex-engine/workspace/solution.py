def match(pattern: str, text: str) -> bool:
    # Parse pattern into list of (element, quantifier) tokens upfront for validation.
    tokens = []
    i = 0
    while i < len(pattern):
        if pattern[i] in ('*', '+', '?'):
            raise ValueError(
                f"Quantifier '{pattern[i]}' at position {i} has no preceding element"
            )

        if pattern[i] == '[':
            i += 1
            negated = False
            if i < len(pattern) and pattern[i] == '^':
                negated = True
                i += 1
            chars = set()
            # A literal ] as the first char inside a class is allowed.
            if i < len(pattern) and pattern[i] == ']':
                chars.add(']')
                i += 1
            while i < len(pattern) and pattern[i] != ']':
                # Range like a-z, but not if '-' is the last char before ']'.
                if (i + 2 < len(pattern)
                        and pattern[i + 1] == '-'
                        and pattern[i + 2] != ']'):
                    lo, hi = ord(pattern[i]), ord(pattern[i + 2])
                    if lo > hi:
                        raise ValueError(
                            f"Invalid character-class range '{pattern[i]}-{pattern[i+2]}'"
                        )
                    chars.update(chr(c) for c in range(lo, hi + 1))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed '[' in pattern")
            i += 1  # skip ']'
            elem = ('class_neg' if negated else 'class', frozenset(chars))
        elif pattern[i] == '.':
            elem = ('any',)
            i += 1
        else:
            elem = ('lit', pattern[i])
            i += 1

        quant = None
        if i < len(pattern) and pattern[i] in ('*', '+', '?'):
            quant = pattern[i]
            i += 1

        tokens.append((elem, quant))

    def matches_elem(elem, c: str) -> bool:
        kind = elem[0]
        if kind == 'any':
            return True
        if kind == 'lit':
            return c == elem[1]
        if kind == 'class':
            return c in elem[1]
        # class_neg
        return c not in elem[1]

    def dp(ti: int, tok_i: int) -> bool:
        """Return True if tokens[tok_i:] match text[ti:]."""
        if tok_i == len(tokens):
            return ti == len(text)

        elem, quant = tokens[tok_i]

        if quant is None:
            return (ti < len(text)
                    and matches_elem(elem, text[ti])
                    and dp(ti + 1, tok_i + 1))

        if quant == '?':
            if ti < len(text) and matches_elem(elem, text[ti]):
                if dp(ti + 1, tok_i + 1):
                    return True
            return dp(ti, tok_i + 1)

        if quant == '+':
            # Must match at least one character.
            if ti >= len(text) or not matches_elem(elem, text[ti]):
                return False
            ti += 1
            # Then zero or more: try rest of pattern at each position.
            while True:
                if dp(ti, tok_i + 1):
                    return True
                if ti < len(text) and matches_elem(elem, text[ti]):
                    ti += 1
                else:
                    return False

        # quant == '*': zero or more.
        while True:
            if dp(ti, tok_i + 1):
                return True
            if ti < len(text) and matches_elem(elem, text[ti]):
                ti += 1
            else:
                return False

    return dp(0, 0)
