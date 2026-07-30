def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)

    def matches_atom(atom, c):
        kind = atom[0]
        if kind == "dot":
            return True
        elif kind == "literal":
            return atom[1] == c
        else:  # class
            negated, ranges = atom[1], atom[2]
            for start, end in ranges:
                if start <= c <= end:
                    return not negated
            return negated

    def backtrack(ti, si):
        while ti < len(tokens):
            atom, quant = tokens[ti]

            if quant is None:
                if si >= len(text) or not matches_atom(atom, text[si]):
                    return False
                ti += 1
                si += 1

            elif quant == "?":
                # Try skipping first (zero matches)
                if backtrack(ti + 1, si):
                    return True
                # Try matching one
                if si < len(text) and matches_atom(atom, text[si]):
                    ti += 1
                    si += 1

            elif quant == "*":
                # Try zero matches first
                if backtrack(ti + 1, si):
                    return True
                # Try one or more (backtracking)
                while si < len(text) and matches_atom(atom, text[si]):
                    si += 1
                    if backtrack(ti + 1, si):
                        return True
                return False

            elif quant == "+":
                # Must match at least one
                if si >= len(text) or not matches_atom(atom, text[si]):
                    return False
                ti += 1
                si += 1
                # Now try zero or more additional (backtracking)
                while True:
                    if backtrack(ti + 1, si):
                        return True
                    if si < len(text) and matches_atom(atom, text[si]):
                        si += 1
                    else:
                        return False

        return si == len(text)

    return backtrack(0, 0)


def _parse_pattern(pattern):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        # Check for quantifier without preceding element
        if c in "*+?" and (not tokens or tokens[-1][2] is not None):
            raise ValueError("Quantifier without preceding element")

        if c == "[":
            i += 1
            negated = False
            if i < n and pattern[i] == "^":
                negated = True
                i += 1

            # Find closing ']'
            close = pattern.find("]", i)
            if close == -1:
                raise ValueError("Unclosed character class")

            inner = pattern[i:close]
            i = close + 1

            # Parse inner content into ranges
            ranges = []
            j = 0
            m = len(inner)
            while j < m:
                if j + 2 < m and inner[j + 1] == "-":
                    start_c = inner[j]
                    end_c = inner[j + 2]
                    ranges.append((start_c, end_c))
                    j += 3
                else:
                    ranges.append((inner[j], inner[j]))
                    j += 1

            atom = ("class", negated, ranges)

        elif c == ".":
            atom = ("dot",)
            i += 1

        else:
            atom = ("literal", c)
            i += 1

        # Check for quantifier after the atom
        if i < n and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1
        else:
            quant = None

        tokens.append((atom, quant))

    return tokens
