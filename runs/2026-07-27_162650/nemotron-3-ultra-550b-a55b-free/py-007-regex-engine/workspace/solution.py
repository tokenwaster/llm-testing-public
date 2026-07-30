def match(pattern: str, text: str) -> bool:
    from functools import lru_cache

    # ---------- parsing helpers ----------
    def parse_class(p: str, i: int):
        """Parse a character class starting at p[i] == '['.
        Returns ((intervals, negated), new_index)."""
        i += 1  # skip '['
        if i >= len(p):
            raise ValueError("Unclosed [")
        negated = False
        if p[i] == '^':
            negated = True
            i += 1
            if i >= len(p):
                raise ValueError("Unclosed [")
        intervals = []
        # empty class like [] or [^]
        if i < len(p) and p[i] == ']':
            raise ValueError("Empty character class")
        while i < len(p) and p[i] != ']':
            # range: x-y where y != ']'
            if i + 2 < len(p) and p[i + 1] == '-' and p[i + 2] != ']':
                start, end = p[i], p[i + 2]
                if ord(start) > ord(end):
                    raise ValueError("Invalid range in character class")
                intervals.append((ord(start), ord(end)))
                i += 3
            else:
                ch = p[i]
                intervals.append((ord(ch), ord(ch)))
                i += 1
        if i >= len(p) or p[i] != ']':
            raise ValueError("Unclosed [")
        i += 1  # skip ']'
        return (intervals, negated), i

    def parse_pattern(p: str):
        """Convert pattern string into a list of tokens.
        Each token is a tuple:
          ('literal', char, quant)
          ('dot', quant)
          ('class', intervals, negated, quant)
        quant is None, '*', '+', or '?'."""
        tokens = []
        i = 0
        while i < len(p):
            if p[i] == '[':
                (intervals, negated), i = parse_class(p, i)
                quant = None
                if i < len(p) and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                tokens.append(('class', intervals, negated, quant))
            elif p[i] == '.':
                i += 1
                quant = None
                if i < len(p) and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                tokens.append(('dot', quant))
            elif p[i] in '*+?':
                raise ValueError("Quantifier with no preceding element")
            else:
                ch = p[i]
                i += 1
                quant = None
                if i < len(p) and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                tokens.append(('literal', ch, quant))
        return tokens

    # ---------- main logic ----------
    if pattern == "":
        return text == ""

    tokens = parse_pattern(pattern)

    @lru_cache(maxsize=None)
    def dp(p_idx: int, t_idx: int) -> bool:
        """Return True iff tokens[p_idx:] matches text[t_idx:]."""
        if p_idx == len(tokens):
            return t_idx == len(text)

        token = tokens[p_idx]
        typ = token[0]
        quant = token[-1]  # last element is always the quantifier

        # element matcher
        if typ == 'literal':
            ch = token[1]
            def matches(c: str) -> bool:
                return c == ch
        elif typ == 'dot':
            def matches(c: str) -> bool:
                return True
        elif typ == 'class':
            intervals, negated = token[1], token[2]
            def matches(c: str) -> bool:
                o = ord(c)
                in_class = any(start <= o <= end for start, end in intervals)
                return in_class != negated
        else:
            raise ValueError("Unknown token type")

        # quantifier handling
        if quant is None:
            if t_idx < len(text) and matches(text[t_idx]):
                return dp(p_idx + 1, t_idx + 1)
            return False

        elif quant == '?':
            # zero occurrences
            if dp(p_idx + 1, t_idx):
                return True
            # one occurrence
            if t_idx < len(text) and matches(text[t_idx]):
                return dp(p_idx + 1, t_idx + 1)
            return False

        elif quant == '*':
            # zero occurrences
            if dp(p_idx + 1, t_idx):
                return True
            # one or more
            k = t_idx
            while k < len(text) and matches(text[k]):
                if dp(p_idx + 1, k + 1):
                    return True
                k += 1
            return False

        elif quant == '+':
            # one or more
            k = t_idx
            while k < len(text) and matches(text[k]):
                if dp(p_idx + 1, k + 1):
                    return True
                k += 1
            return False

        else:
            raise ValueError("Unknown quantifier")

    return dp(0, 0)
