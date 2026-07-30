def match(pattern: str, text: str) -> bool:
    """Match pattern against the entire text using a small regex subset.

    Supports:
      - literal characters
      - '.' (any single character)
      - '*' (zero or more of preceding element)
      - '+' (one or more of preceding element)
      - '?' (zero or one of preceding element)
      - character classes [abc], ranges [a-z0-9], negation [^abc]
      - quantifiers may follow a class

    Malformed patterns raise ValueError.
    """
    # ---------- parsing ----------
    tokens = []  # list of (match_func, quantifier)
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        # quantifiers must follow an element
        if c in '*+?':
            raise ValueError(f"Nothing to quantify before '{c}'")

        # parse one element
        if c == '.':
            match_func = lambda ch: True
            i += 1
        elif c == '[':
            i += 1
            if i >= n:
                raise ValueError("Unclosed '['")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
                if i >= n:
                    raise ValueError("Unclosed '['")
            content_start = i
            allowed = set()
            # ']' as the very first character is a literal
            if i < n and pattern[i] == ']':
                allowed.add(']')
                i += 1
                if i >= n:
                    raise ValueError("Unclosed '['")
            while i < n and pattern[i] != ']':
                ch = pattern[i]
                # check for range like a-z
                if ch == '-' and i > content_start and i + 1 < n and pattern[i + 1] != ']':
                    lo = pattern[i - 1]
                    hi = pattern[i + 1]
                    if ord(lo) > ord(hi):
                        raise ValueError(f"Invalid range {lo}-{hi}")
                    for code in range(ord(lo), ord(hi) + 1):
                        allowed.add(chr(code))
                    i += 2  # skip the dash and the high character
                    continue
                else:
                    allowed.add(ch)
                    i += 1
            if i >= n:
                raise ValueError("Unclosed '['")
            i += 1  # skip the closing ']'

            if negated:
                match_func = lambda ch, allowed=allowed: ch not in allowed
            else:
                match_func = lambda ch, allowed=allowed: ch in allowed
        else:
            # literal character
            lit = c
            match_func = lambda ch, lit=lit: ch == lit
            i += 1

        # optional quantifier
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        tokens.append((match_func, quant))

    # ---------- matching (recursive backtracking, greedy) ----------
    n_text = len(text)

    def match_star(idx: int, pos: int) -> bool:
        """Greedy match of zero or more of tokens[idx]."""
        match_func, _ = tokens[idx]
        if pos < n_text and match_func(text[pos]):
            if match_star(idx, pos + 1):
                return True
        return match_tokens(idx + 1, pos)

    def match_tokens(idx: int, pos: int) -> bool:
        if idx == len(tokens):
            return pos == n_text
        match_func, quant = tokens[idx]
        if quant is None:
            if pos < n_text and match_func(text[pos]):
                return match_tokens(idx + 1, pos + 1)
            return False
        elif quant == '?':
            # zero or one (greedy: try one first)
            if pos < n_text and match_func(text[pos]):
                if match_tokens(idx + 1, pos + 1):
                    return True
            return match_tokens(idx + 1, pos)
        elif quant == '*':
            return match_star(idx, pos)
        elif quant == '+':
            if pos < n_text and match_func(text[pos]):
                return match_star(idx, pos + 1)
            return False
        else:
            raise ValueError(f"Unknown quantifier {quant}")

    return match_tokens(0, 0)
