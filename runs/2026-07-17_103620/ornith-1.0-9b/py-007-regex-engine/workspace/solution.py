def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)
    return _match(tokens, text)


def _parse_pattern(pattern):
    i = 0
    n = len(pattern)
    tokens = []

    while i < n:
        if pattern[i] in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{pattern[i]}' without preceding element")

        # Parse atom (literal, wildcard, or character class)
        if pattern[i] == '[':
            j = i + 1
            if j >= n or pattern[j] == ']':
                raise ValueError("Empty character class '[]'")

            negated = False
            if pattern[j] == '^':
                negated = True
                j += 1

            chars = set()
            while j < n and pattern[j] != ']':
                c = pattern[j]
                # Check for range like a-z
                if (c == '-' and j + 1 < n
                    and pattern[j + 1] != ']'
                    and pattern[j + 1] != '^'):
                    j += 1
                    end_c = pattern[j]
                    start_ord, end_ord = ord(pattern[j - 1]), ord(end_c)
                    for code in range(start_ord, end_ord + 1):
                        chars.add(chr(code))
                    j += 1
                else:
                    chars.add(c)
                    j += 1

            if j >= n:
                raise ValueError("Unclosed character class")

            i = j + 1  # skip past ']'

            atom_type = 'class'
            atom_value = (negated, frozenset(chars))
        elif pattern[i] == '.':
            i += 1
            atom_type = 'wildcard'
            atom_value = None
        else:
            atom_type = 'literal'
            atom_value = pattern[i]
            i += 1

        # Check for quantifier after atom
        quantifier = None
        if i < n and pattern[i] in ('*', '+', '?'):
            quantifier = pattern[i]
            i += 1

        tokens.append((atom_type, atom_value, quantifier))

    return tokens


def _match(tokens, text):
    if not tokens:
        return text == ''

    atom_type, atom_value, quantifier = tokens[0]
    rest_tokens = tokens[1:]

    def matches_one():
        """Check if current char of text matches this atom."""
        if not text:
            return False
        c = text[0]

        if atom_type == 'literal':
            return c == atom_value
        elif atom_type == 'wildcard':
            return True
        elif atom_type == 'class':
            negated, chars = atom_value
            if negated:
                return c not in chars
            else:
                return c in chars

    if quantifier is None:
        # Must match exactly once
        if matches_one():
            return _match(rest_tokens, text[1:])
        return False

    elif quantifier == '*':
        # Zero or more of the preceding element
        return _match_star(atom_type, atom_value, rest_tokens, text)

    elif quantifier == '+':
        # One or more of the preceding element
        if not matches_one():
            return False
        return _match_star(atom_type, atom_value, rest_tokens, text[1:])

    elif quantifier == '?':
        # Zero or one of the preceding element
        result = _match(rest_tokens, text)  # zero times
        if result:
            return True
        if matches_one():
            return _match(rest_tokens, text[1:])  # one time
        return False

    return False


def _match_star(atom_type, atom_value, rest_tokens, text):
    """Match zero or more of the given atom."""
    # Option 0: don't match any, move to next token
    if _match(rest_tokens, text):
        return True

    # Option 1+: match one and try again (recursively)
    if matches_one():
        return _match_star(atom_type, atom_value, rest_tokens, text[1:])

    return False


def _match_plus(atom_type, atom_value, rest_tokens, text):
    """Match one or more of the given atom."""
    # Must match at least one
    if not matches_one():
        return False

    # Now try matching zero or more (same as star but we already matched one)
    return _match_star(atom_type, atom_value, rest_tokens, text[1:])
