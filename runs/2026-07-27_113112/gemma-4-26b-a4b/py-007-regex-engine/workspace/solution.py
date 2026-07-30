def match(pattern: str, text: str) -> bool:
    """
    Matches a pattern against the entire text using a subset of regex syntax.
    Supports '.', '*', '+', '?', and character classes [abc], [a-z0-9], [^abc].
    """
    
    def parse_pattern(pattern):
        tokens = []
        i = 0
        n = len(pattern)
        while i < n:
            char = pattern[i]
            # If a quantifier appears at the start of a token, it's malformed.
            if char in '*+?':
                raise ValueError("Quantifier without preceding element")
            
            matcher = None
            if char == '[':
                i += 1
                negated = False
                if i < n and pattern[i] == '^':
                    negated = True
                    i += 1
                
                chars_in_class = set()
                found_end = False
                while i < n:
                    if pattern[i] == ']':
                        found_end = True
                        i += 1
                        break
                    # Check for ranges like [a-z]
                    if (i + 2 < n and pattern[i+1] == '-' and 
                        pattern[i+2] != ']' and pattern[i+2] != '^'):
                        start_c = pattern[i]
                        end_c = pattern[i+2]
                        for c_code in range(ord(start_c), ord(end_c) + 1):
                            chars_in_class.add(chr(c_code))
                        i += 3
                    else:
                        chars_in_class.add(pattern[i])
                        i += 1
                
                if not found_end:
                    raise ValueError("Unclosed character class")
                
                # Closure to capture the current set and negation state
                def make_matcher(c_set, neg):
                    return lambda c: (c in c_set) != neg
                matcher = make_matcher(chars_in_class, negated)

            elif char == '.':
                matcher = lambda c: True
                i += 1
            else:
                # Literal character
                lit_char = char
                matcher = (lambda c, lc=lit_char: c == lc)
                i += 1
            
            # Check for quantifier following the matcher
            quantifier = None
            if i < n and pattern[i] in '*+?':
                quantifier = pattern[i]
                i += 1
            
            tokens.append((matcher, quantifier))

        # Transform '+' into (None) followed by ('*') to simplify backtracking logic
        new_tokens = []
        for m, q in tokens:
            if q == '+':
                new_tokens.append((m, None))
                new_tokens.append((m, '*'))
            else:
                new_tokens.append((m, q))
        return new_tokens

    # Parse the pattern into a list of (matcher, quantifier) tuples
    try:
        processed_tokens = parse_pattern(pattern)
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError("Malformed pattern") from e

    def backtrack(t_idx, txt_idx):
        # If all tokens have been processed, check if the entire text was matched
        if t_idx == len(processed_tokens):
            return txt_idx == len(text)
        
        m, q = processed_tokens[t_idx]
        
        if q is None:
            # Exactly one character must match
            if txt_idx < len(text) and m(text[txt_idx]):
                return backtrack(t_idx + 1, txt_idx + 1)
            return False
            
        elif q == '?':
            # Zero or one character can match
            # Case 1: Match one character (if possible)
            if txt_idx < len(text) and m(text[txt_idx]):
                if backtrack(t_idx + 1, txt_idx + 1):
                    return True
            # Case 2: Skip this token entirely
            return backtrack(t_idx + 1, txt_idx)
            
        elif q == '*':
            # Zero or more characters can match
            # Case 1: Match zero (skip this token)
            if backtrack(t_idx + 1, txt_idx):
                return True
            # Case 2: Match one and continue with the same '*' token
            if txt_idx < len(text) and m(text[txt_idx]):
                if backtrack(t_idx, txt_idx + 1):
                    return True
            return False
        
        return False

    return backtrack(0, 0)
