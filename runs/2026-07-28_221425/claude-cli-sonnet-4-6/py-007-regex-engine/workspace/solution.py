def match(pattern: str, text: str) -> bool:
    n = len(pattern)

    def parse_class(pi):
        """Parse a [...] class starting at pi. Returns (match_fn, end_pi)."""
        i = pi + 1
        if i >= n:
            raise ValueError("Unclosed character class '['")

        negate = False
        if pattern[i] == '^':
            negate = True
            i += 1

        chars = set()
        ranges = []
        first_in_class = True

        while i < n and (pattern[i] != ']' or first_in_class):
            first_in_class = False
            if i + 2 < n and pattern[i + 1] == '-' and pattern[i + 2] != ']':
                ranges.append((pattern[i], pattern[i + 2]))
                i += 3
            else:
                chars.add(pattern[i])
                i += 1

        if i >= n:
            raise ValueError("Unclosed character class '['")

        end_pi = i + 1  # skip ']'

        def matches_class(c):
            result = (c in chars) or any(lo <= c <= hi for lo, hi in ranges)
            return (not result) if negate else result

        return matches_class, end_pi

    def dp(pi, ti):
        if pi == n:
            return ti == len(text)

        if pattern[pi] in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{pattern[pi]}' without preceding element")

        # Parse the current atom.
        if pattern[pi] == '[':
            atom_fn, next_pi = parse_class(pi)
        elif pattern[pi] == '.':
            atom_fn = lambda c: True
            next_pi = pi + 1
        else:
            ch = pattern[pi]
            atom_fn = lambda c, _ch=ch: c == _ch
            next_pi = pi + 1

        # Check for a following quantifier.
        if next_pi < n and pattern[next_pi] in ('*', '+', '?'):
            quant = pattern[next_pi]
            after = next_pi + 1

            if quant == '?':
                if ti < len(text) and atom_fn(text[ti]):
                    if dp(after, ti + 1):
                        return True
                return dp(after, ti)

            elif quant == '*':
                end = ti
                while end < len(text) and atom_fn(text[end]):
                    end += 1
                for j in range(end, ti - 1, -1):
                    if dp(after, j):
                        return True
                return False

            else:  # '+'
                if ti >= len(text) or not atom_fn(text[ti]):
                    return False
                end = ti + 1
                while end < len(text) and atom_fn(text[end]):
                    end += 1
                for j in range(end, ti, -1):
                    if dp(after, j):
                        return True
                return False

        else:
            # No quantifier: consume exactly one character.
            if ti < len(text) and atom_fn(text[ti]):
                return dp(next_pi, ti + 1)
            return False

    return dp(0, 0)
