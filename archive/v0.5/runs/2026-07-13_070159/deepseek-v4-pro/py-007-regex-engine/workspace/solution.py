def match(pattern: str, text: str) -> bool:
    """
    Returns True if the regex pattern matches the entire text.
    Supports: literal characters, . (any), * (0 or more), + (1 or more),
    ? (0 or 1), character classes [abc], ranges [a-z0-9], negation [^abc].
    Malformed patterns raise ValueError.
    """
    # Tokenization
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c in '*+?':
            raise ValueError("unexpected quantifier")
        elif c == '.':
            quant = None
            if i + 1 < n and pattern[i+1] in '*+?':
                quant = pattern[i+1]
                i += 1
            tokens.append(('dot', None, quant))
            i += 1
        elif c == '[':
            # find closing bracket
            j = i + 1
            while j < n and pattern[j] != ']':
                j += 1
            if j == n:
                raise ValueError("unclosed character class")
            content = pattern[i+1:j]
            negate = False
            if content.startswith('^'):
                negate = True
                content = content[1:]
            if not content:
                raise ValueError("empty character class")
            # parse content into set of characters
            chars = set()
            k = 0
            while k < len(content):
                if k + 2 < len(content) and content[k+1] == '-':
                    start_c = content[k]
                    end_c = content[k+2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError(f"invalid range: {start_c}-{end_c}")
                    for code in range(ord(start_c), ord(end_c) + 1):
                        chars.add(chr(code))
                    k += 3
                else:
                    chars.add(content[k])
                    k += 1
            # quantifier after class?
            i = j + 1  # after ']'
            quant = None
            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            tokens.append(('class', (negate, chars), quant))
        else:
            # literal character (including ']')
            literal = c
            quant = None
            if i + 1 < n and pattern[i+1] in '*+?':
                quant = pattern[i+1]
                i += 1
            tokens.append(('literal', literal, quant))
            i += 1

    # Helper to test a single character against a token
    def matches_char(tok, ch):
        if tok[0] == 'dot':
            return True
        elif tok[0] == 'literal':
            return tok[1] == ch
        elif tok[0] == 'class':
            negate, chars = tok[1]
            return (ch not in chars) if negate else (ch in chars)
        else:
            return False

    # Recursive backtracking matcher
    def match_tokens(tok_idx, txt_idx):
        if tok_idx == len(tokens):
            return txt_idx == len(text)
        tok = tokens[tok_idx]
        quant = tok[2]
        if quant is None:
            if txt_idx >= len(text):
                return False
            if not matches_char(tok, text[txt_idx]):
                return False
            return match_tokens(tok_idx + 1, txt_idx + 1)
        elif quant == '?':
            # zero
            if match_tokens(tok_idx + 1, txt_idx):
                return True
            # one
            if txt_idx < len(text) and matches_char(tok, text[txt_idx]):
                return match_tokens(tok_idx + 1, txt_idx + 1)
            return False
        elif quant == '*':
            # zero
            if match_tokens(tok_idx + 1, txt_idx):
                return True
            # more
            idx = txt_idx
            while idx < len(text) and matches_char(tok, text[idx]):
                idx += 1
                if match_tokens(tok_idx + 1, idx):
                    return True
            return False
        elif quant == '+':
            # must match at least one
            if txt_idx >= len(text) or not matches_char(tok, text[txt_idx]):
                return False
            idx = txt_idx + 1
            while True:
                if match_tokens(tok_idx + 1, idx):
                    return True
                if idx < len(text) and matches_char(tok, text[idx]):
                    idx += 1
                else:
                    break
            return False
        else:
            raise ValueError("unknown quantifier")

    return match_tokens(0, 0)
