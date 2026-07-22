def match(pattern: str, text: str) -> bool:
    def parse(pattern: str):
        tokens = []
        i = 0
        n = len(pattern)
        while i < n:
            if pattern[i] == '[':
                j = i + 1
                if j >= n:
                    raise ValueError("unclosed character class")
                negate = False
                if pattern[j] == '^':
                    negate = True
                    j += 1
                chars = set()
                while j < n and pattern[j] != ']':
                    if (j + 2 < n and pattern[j + 1] == '-' and
                            pattern[j + 2] != ']'):
                        start_c = pattern[j]
                        end_c = pattern[j + 2]
                        if ord(start_c) > ord(end_c):
                            raise ValueError("invalid range in character class")
                        for code in range(ord(start_c), ord(end_c) + 1):
                            chars.add(chr(code))
                        j += 3
                    else:
                        chars.add(pattern[j])
                        j += 1
                if j >= n or pattern[j] != ']':
                    raise ValueError("unclosed character class")
                atom = ('class', negate, frozenset(chars))
                i = j + 1
            elif pattern[i] == '.':
                atom = ('dot',)
                i += 1
            elif pattern[i] in '*+?':
                raise ValueError("quantifier without preceding element")
            else:
                atom = ('lit', pattern[i])
                i += 1

            quant = '1'
            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            tokens.append((atom, quant))
        return tokens

    def match_atom(atom, ch: str) -> bool:
        kind = atom[0]
        if kind == 'lit':
            return atom[1] == ch
        if kind == 'dot':
            return True
        # class
        _, negate, chars = atom
        return (ch in chars) != negate

    def match_tokens(tokens, ti: int, s: str, si: int) -> bool:
        if ti == len(tokens):
            return si == len(s)
        atom, quant = tokens[ti]

        if quant == '1':
            if si < len(s) and match_atom(atom, s[si]):
                return match_tokens(tokens, ti + 1, s, si + 1)
            return False

        if quant == '?':
            if si < len(s) and match_atom(atom, s[si]):
                if match_tokens(tokens, ti + 1, s, si + 1):
                    return True
            return match_tokens(tokens, ti + 1, s, si)

        # * or +
        if quant == '+':
            if not (si < len(s) and match_atom(atom, s[si])):
                return False
            si += 1
            # fall through to * logic from here

        # * (zero or more), greedy backtracking
        while True:
            if match_tokens(tokens, ti + 1, s, si):
                return True
            if si < len(s) and match_atom(atom, s[si]):
                si += 1
            else:
                break
        return False

    tokens = parse(pattern)
    return match_tokens(tokens, 0, text, 0)
