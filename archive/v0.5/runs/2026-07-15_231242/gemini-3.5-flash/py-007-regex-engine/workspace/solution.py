def match(pattern: str, text: str) -> bool:
    # Parse the pattern into a list of tokens.
    # A token is either:
    # - ('char', c): matches character c
    # - ('dot',): matches any character
    # - ('class', set_of_chars, negated): matches any character in/not in the set
    # Each token can be followed by a quantifier: None, '*', '+', or '?'
    tokens = []
    i = 0
    n = len(pattern)
    
    while i < n:
        char = pattern[i]
        if char in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{char}' without preceding element")
        elif char == '.':
            tokens.append(('dot',))
            i += 1
        elif char == '[':
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
                if i >= n:
                    raise ValueError("Unclosed character class")
            
            # Read class contents until ']'
            class_chars = set()
            start_idx = i
            while i < n and pattern[i] != ']':
                # Check for range
                if i + 2 < n and pattern[i+1] == '-' and pattern[i+2] != ']':
                    start_c = pattern[i]
                    end_c = pattern[i+2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError(f"Invalid range {start_c}-{end_c}")
                    for c_code in range(ord(start_c), ord(end_c) + 1):
                        class_chars.add(chr(c_code))
                    i += 3
                else:
                    class_chars.add(pattern[i])
                    i += 1
            
            if i >= n or pattern[i] != ']':
                raise ValueError("Unclosed character class")
            i += 1 # skip ']'
            tokens.append(('class', class_chars, negated))
        else:
            tokens.append(('char', char))
            i += 1
            
        # Check if a quantifier follows the token we just added
        if i < n and pattern[i] in ('*', '+', '?'):
            quant = pattern[i]
            i += 1
            # Attach quantifier to the last token
            last_tok = tokens.pop()
            tokens.append((last_tok, quant))
        else:
            last_tok = tokens.pop()
            tokens.append((last_tok, None))

    # Helper to check if a base token matches a single character
    def match_token_char(tok, char: str) -> bool:
        tok_type = tok[0]
        if tok_type == 'char':
            return tok[1] == char
        elif tok_type == 'dot':
            return True
        elif tok_type == 'class':
            _, chars_set, negated = tok
            is_in = char in chars_set
            return not is_in if negated else is_in
        return False

    # Backtracking matcher
    # t_idx: index in tokens
    # s_idx: index in text
    memo = {}
    def backtrack(t_idx: int, s_idx: int) -> bool:
        state = (t_idx, s_idx)
        if state in memo:
            return memo[state]
        
        if t_idx == len(tokens):
            res = (s_idx == len(text))
            memo[state] = res
            return res
            
        tok, quant = tokens[t_idx]
        
        if quant is None:
            if s_idx < len(text) and match_token_char(tok, text[s_idx]):
                res = backtrack(t_idx + 1, s_idx + 1)
            else:
                res = False
        elif quant == '?':
            # Option 1: match 0 times
            if backtrack(t_idx + 1, s_idx):
                res = True
            # Option 2: match 1 time
            elif s_idx < len(text) and match_token_char(tok, text[s_idx]) and backtrack(t_idx + 1, s_idx + 1):
                res = True
            else:
                res = False
        elif quant == '*':
            # Option 1: match 0 times and move to next token
            if backtrack(t_idx + 1, s_idx):
                res = True
            # Option 2: match 1 time and stay on this '*' token to match more
            elif s_idx < len(text) and match_token_char(tok, text[s_idx]) and backtrack(t_idx, s_idx + 1):
                res = True
            else:
                res = False
        elif quant == '+':
            # Must match at least once.
            # This is equivalent to matching once, then treating it as '*'
            if s_idx < len(text) and match_token_char(tok, text[s_idx]):
                # After matching one, we can either stop (move to t_idx + 1) or continue matching (stay at t_idx with '*' behavior)
                # To implement this cleanly: we can transition to a state where we treat this as a '*' quantifier.
                # We can simulate the '*' behavior by trying to match more of the same token.
                if backtrack(t_idx + 1, s_idx + 1) or backtrack(t_idx, s_idx + 1):
                    res = True
                else:
                    res = False
            else:
                res = False
        else:
            res = False
            
        memo[state] = res
        return res

    return backtrack(0, 0)
