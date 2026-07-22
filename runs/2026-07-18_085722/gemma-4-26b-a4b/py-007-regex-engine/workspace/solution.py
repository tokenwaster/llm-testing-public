def match(pattern: str, text: str) -> bool:
    """
    Matches the entire text against a regex pattern supporting literals, '.', 
    '*', '+', '?', and character classes [abc], [a-z], [^abc].
    """

    def parse_pattern(pattern):
        tokens = []
        i = 0
        if not pattern:
            return []
        if pattern[0] in '*+?':
            raise ValueError("Leading quantifier")

        while i < len(pattern):
            atom = None
            # 1. Parse Atom (Literal, '.', or Character Class)
            if pattern[i] == '[':
                start_idx = i
                i += 1
                negate = False
                if i < len(pattern) and pattern[i] == '^':
                    negate = True
                    i += 1

                content_start = i
                while i < len(pattern) and pattern[i] != ']':
                    i += 1

                if i >= len(pattern):
                    raise ValueError("Unclosed '['")

                class_content = pattern[content_start:i]
                chars = set()
                j = 0
                while j < len(class_content):
                    # Handle ranges like a-z
                    if j + 2 < len(class_content) and class_content[j+1] == '-':
                        try:
                            start_c = ord(class_content[j])
                            end_c = ord(class_content[j+2])
                            for code in range(start_c, end_c + 1):
                                chars.add(chr(code))
                            j += 3
                        except (ValueError, IndexError):
                            # Fallback for malformed ranges if necessary
                            chars.add(class_content[j])
                            j += 1
                    else:
                        chars.add(class_content[j])
                        j += 1

                def make_pred(c_set, neg):
                    return lambda char: (char in c_set) != neg
                atom = make_pred(chars, negate)
                i += 1  # Skip ']'
            elif pattern[i] == '.':
                atom = lambda char: True
                i += 1
            else:
                char = pattern[i]
                atom = lambda char, c=char: char == c
                i += 1

            if atom is None:
                raise ValueError("Malformed pattern")

            # 2. Parse Quantifier (*, +, ?)
            quantifier = '1'
            if i < len(pattern) and pattern[i] in '*+?':
                quantifier = pattern[i]
                i += 1
                if i < len(pattern) and pattern[i] in '*+?':
                    raise ValueError("Consecutive quantifiers")

            # 3. Transform Quantifiers into simple atoms for backtracking
            # '+' is treated as '1' followed by '*'
            if quantifier == '+':
                tokens.append((atom, '1'))
                tokens.append((atom, '*'))
            elif quantifier == '*':
                tokens.append((atom, '*'))
            elif quantifier == '?':
                tokens.append((atom, '?'))
            else:
                tokens.append((atom, '1'))

        return tokens

    tokens = parse_pattern(pattern)

    def backtrack(t_idx, s_idx):
        # Base case: all tokens processed
        if t_idx == len(tokens):
            return s_idx == len(text)

        atom, q = tokens[t_idx]

        if q == '1':
            # Exactly one match required
            if s_idx < len(text) and atom(text[s_idx]):
                return backtrack(t_idx + 1, s_idx + 1)
            return False

        elif q == '?':
            # Zero or one match
            # Option 1: Skip the token
            if backtrack(t_idx + 1, s_idx):
                return True
            # Option 2: Use the token once
            if s_idx < len(text) and atom(text[s_idx]):
                return backtrack(t_idx + 1, s_idx + 1)
            return False

        elif q == '*':
            # Zero or more matches
            # Option 1: Skip the token (zero matches)
            if backtrack(t_idx + 1, s_idx):
                return True
            # Option 2: Match one and stay on this '*' token
            if s_idx < len(text) and atom(text[s_idx]):
                return backtrack(t_idx, s_idx + 1)
            return False

        return False

    return backtrack(0, 0)
