def match(pattern: str, text: str) -> bool:
    """
    Returns True if pattern matches the entire text, using a simple recursive
    backtracking regex engine. Supports: literals, '.', '*', '+', '?',
    character classes with ranges and negation.
    """
    # Parse pattern into a list of tokens.
    # Each token is a tuple: (type, data)
    # Types:
    #   'literal' -> data is the character
    #   'dot' -> data is None
    #   'star' -> data is the preceding token (which can be literal, dot, or class)
    #   'plus' -> data is the preceding token
    #   'question' -> data is the preceding token
    #   'class' -> data is a dict with 'chars' (set of individual chars),
    #              'ranges' (list of (start, end) tuples), 'negated' (bool)
    tokens = _tokenize(pattern)

    # Use recursive backtracking to match tokens against text.
    def _match_tokens(tok_idx, text_pos):
        # If we've consumed all tokens and all text, success.
        if tok_idx == len(tokens):
            return text_pos == len(text)
        # If we are beyond text but still have tokens, fail (unless tokens can match empty).
        if text_pos > len(text):
            return False

        token = tokens[tok_idx]

        if token[0] == 'literal':
            ch = token[1]
            if text_pos < len(text) and text[text_pos] == ch:
                return _match_tokens(tok_idx + 1, text_pos + 1)
            return False

        elif token[0] == 'dot':
            if text_pos < len(text):
                return _match_tokens(tok_idx + 1, text_pos + 1)
            return False

        elif token[0] == 'class':
            cls = token[1]
            if text_pos < len(text):
                c = text[text_pos]
                if _char_in_class(c, cls):
                    return _match_tokens(tok_idx + 1, text_pos + 1)
            return False

        elif token[0] == 'star':
            # zero or more of the preceding element
            # We try zero match first, then expand
            inner = token[1]
            # Try zero matches
            if _match_tokens(tok_idx + 1, text_pos):
                return True
            # Try one or more matches (greedy)
            saved_pos = text_pos
            while True:
                # Try to match the inner token at current position
                if inner[0] == 'literal':
                    if text_pos < len(text) and text[text_pos] == inner[1]:
                        text_pos += 1
                    else:
                        break
                elif inner[0] == 'dot':
                    if text_pos < len(text):
                        text_pos += 1
                    else:
                        break
                elif inner[0] == 'class':
                    if text_pos < len(text) and _char_in_class(text[text_pos], inner[1]):
                        text_pos += 1
                    else:
                        break
                else:
                    # Should not happen (inner of star must be simple)
                    break
                # After consuming, check if rest matches with star continuing
                if _match_tokens(tok_idx + 1, text_pos):
                    return True
            # If no expansion leads to success, restore and fail
            text_pos = saved_pos
            return False

        elif token[0] == 'plus':
            # One or more of preceding element
            inner = token[1]
            # Must match at least once
            if inner[0] == 'literal':
                if text_pos >= len(text) or text[text_pos] != inner[1]:
                    return False
                text_pos += 1
            elif inner[0] == 'dot':
                if text_pos >= len(text):
                    return False
                text_pos += 1
            elif inner[0] == 'class':
                if text_pos >= len(text) or not _char_in_class(text[text_pos], inner[1]):
                    return False
                text_pos += 1
            else:
                return False
            # Now treat as star (zero or more) of the same inner
            # Build a star token on the fly and recurse
            star_token = ('star', inner)
            # Insert the star token at the current position, consume rest
            return _match_star_after_plus(star_token, tok_idx + 1, text_pos, tokens, _match_tokens)

        elif token[0] == 'question':
            # Zero or one of preceding element
            inner = token[1]
            # Try zero first
            if _match_tokens(tok_idx + 1, text_pos):
                return True
            # Try one match
            if inner[0] == 'literal':
                if text_pos < len(text) and text[text_pos] == inner[1]:
                    return _match_tokens(tok_idx + 1, text_pos + 1)
            elif inner[0] == 'dot':
                if text_pos < len(text):
                    return _match_tokens(tok_idx + 1, text_pos + 1)
            elif inner[0] == 'class':
                if text_pos < len(text) and _char_in_class(text[text_pos], inner[1]):
                    return _match_tokens(tok_idx + 1, text_pos + 1)
            return False

        return False

    # Helper to match star after plus consumed first char
    def _match_star_after_plus(star_token, tok_idx, text_pos, tokens, orig_match):
        # Same as star matching logic but inline to avoid recursion depth issues
        # Try zero matches of star
        if orig_match(tok_idx, text_pos):
            return True
        inner = star_token[1]
        while True:
            if inner[0] == 'literal':
                if text_pos < len(text) and text[text_pos] == inner[1]:
                    text_pos += 1
                else:
                    break
            elif inner[0] == 'dot':
                if text_pos < len(text):
                    text_pos += 1
                else:
                    break
            elif inner[0] == 'class':
                if text_pos < len(text) and _char_in_class(text[text_pos], inner[1]):
                    text_pos += 1
                else:
                    break
            else:
                break
            if orig_match(tok_idx, text_pos):
                return True
        return False

    return _match_tokens(0, 0)


def _char_in_class(c: str, cls: dict) -> bool:
    """Check if character c is in the character class description."""
    in_class = False
    if c in cls['chars']:
        in_class = True
    for lo, hi in cls['ranges']:
        if lo <= c <= hi:
            in_class = True
            break
    if cls['negated']:
        return not in_class
    return in_class


def _tokenize(pattern: str) -> list:
    """Parse pattern string into tokens. Raises ValueError on malformed patterns."""
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]
        if ch == '\\':
            # Escape sequence: next character is literal
            if i + 1 >= n:
                raise ValueError("Trailing backslash")
            tokens.append(('literal', pattern[i+1]))
            i += 2
        elif ch == '.':
            tokens.append(('dot', None))
            i += 1
        elif ch == '*':
            if not tokens:
                raise ValueError("Star with nothing before it")
            prev = tokens.pop()
            # The previous token must be a base token (literal, dot, or class)
            if prev[0] in ('star', 'plus', 'question'):
                raise ValueError("Invalid preceding element for star")
            tokens.append(('star', prev))
            i += 1
        elif ch == '+':
            if not tokens:
                raise ValueError("Plus with nothing before it")
            prev = tokens.pop()
            if prev[0] in ('star', 'plus', 'question'):
                raise ValueError("Invalid preceding element for plus")
            tokens.append(('plus', prev))
            i += 1
        elif ch == '?':
            if not tokens:
                raise ValueError("Question with nothing before it")
            prev = tokens.pop()
            if prev[0] in ('star', 'plus', 'question'):
                raise ValueError("Invalid preceding element for question")
            tokens.append(('question', prev))
            i += 1
        elif ch == '[':
            # Parse character class
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
            chars = set()
            ranges = []
            # Parse until ']' or end
            while i < n and pattern[i] != ']':
                if i + 2 < n and pattern[i+1] == '-':
                    # It's a range unless the dash is at start/end of class
                    lo = pattern[i]
                    hi = pattern[i+2]
                    # Validate range
                    if lo > hi:
                        raise ValueError("Invalid character range")
                    ranges.append((lo, hi))
                    i += 3
                else:
                    # Single character, possibly escaped
                    if pattern[i] == '\\':
                        if i+1 >= n:
                            raise ValueError("Unclosed character class with escape")
                        chars.add(pattern[i+1])
                        i += 2
                    else:
                        chars.add(pattern[i])
                        i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            # Skip closing ]
            i += 1
            cls_data = {
                'chars': chars,
                'ranges': ranges,
                'negated': negated
            }
            tokens.append(('class', cls_data))
        else:
            # Literal character
            tokens.append(('literal', ch))
            i += 1

    return tokens
