def match(pattern: str, text: str) -> bool:
    """
    Match a pattern against an entire text using recursive backtracking.
    
    Supports: literals, '.', '*', '+', '?', and character classes [abc], [a-z0-9], [^abc]
    """
    if not isinstance(pattern, str) or not isinstance(text, str):
        raise TypeError("Pattern and text must be strings")
    
    def parse_class(pattern_str, i):
        """Parse a character class starting at position i (after the opening '[')."""
        if i >= len(pattern_str):
            raise ValueError("Unclosed character class in pattern")
        
        if pattern_str[i] == '^':
            # Negated character class
            i += 1
            negated = True
            if i >= len(pattern_str):
                raise ValueError("Unclosed character class in pattern")
        else:
            negated = False
        
        chars = set()
        while i < len(pattern_str) and pattern_str[i] != ']':
            # Check for range
            if i + 2 < len(pattern_str) and pattern_str[i+1] == '-' and pattern_str[i+2] != ']':
                start_char = pattern_str[i]
                end_char = pattern_str[i+2]
                if start_char > end_char:
                    raise ValueError(f"Invalid character range: {start_char}-{end_char}")
                for c in range(ord(start_char), ord(end_char) + 1):
                    chars.add(chr(c))
                i += 3
            else:
                chars.add(pattern_str[i])
                i += 1
        
        if i >= len(pattern_str):
            raise ValueError("Unclosed character class in pattern")
        
        return chars, negated, i + 1  # Return the set, whether it's negated, and position after ']'
    
    def compile_pattern(pattern_str):
        """Compile pattern into a list of tokens for easier processing."""
        tokens = []
        i = 0
        
        while i < len(pattern_str):
            c = pattern_str[i]
            
            if c == '[':
                # Start of character class
                chars, negated, next_i = parse_class(pattern_str, i + 1)
                tokens.append(('class', chars, negated))
                i = next_i
                
            elif c in '*+?':
                raise ValueError(f"Modifier '{c}' must follow a pattern element")
                
            elif c == '.':
                tokens.append(('any',))
                i += 1
                
            else:  # literal character
                tokens.append(('literal', c))
                i += 1
            
            # Check for quantifiers following the token we just added
            if i < len(pattern_str):
                next_c = pattern_str[i]
                if next_c in '*+?':
                    if not tokens:
                        raise ValueError(f"Modifier '{next_c}' must follow a pattern element")
                    
                    last_token = tokens.pop()
                    quantifier = next_c
                    
                    # Create new token with quantifier
                    if last_token[0] == 'class':
                        _, chars, negated = last_token
                        tokens.append(('quant_class', chars, negated, quantifier))
                    elif last_token[0] == 'any':
                        tokens.append(('quant_any', quantifier))
                    else:  # literal
                        _, char = last_token
                        tokens.append(('quant_literal', char, quantifier))
                    
                    i += 1
        
        return tokens
    
    try:
        tokens = compile_pattern(pattern)
    except ValueError as e:
        raise e
    
    def match_tokens(tokens_idx, text_idx):
        """Recursively match tokens against text."""
        # Base case: if we've consumed all tokens, check if we've consumed all text
        if tokens_idx == len(tokens):
            return text_idx == len(text)
        
        token = tokens[tokens_idx]
        quantifier = None
        
        # Check for quantifiers in current token
        if token[0] == 'quant_any':
            quantifier = token[1]
        elif token[0] == 'quant_literal':
            quantifier = token[2]
        elif token[0] == 'quant_class':
            quantifier = token[3]
        
        # Handle tokens with quantifiers
        if quantifier:
            if quantifier == '*':  # Zero or more
                # Try matching zero occurrences first
                if match_tokens(tokens_idx + 1, text_idx):
                    return True
                
                # Try matching one or more
                if token[0] == 'quant_any':
                    # '.' matches any character
                    for k in range(text_idx, len(text) + 1):
                        # Try to match from text_idx to k (at least 1 char)
                        if k > text_idx and match_tokens(tokens_idx + 1, k):
                            return True
                elif token[0] == 'quant_literal':
                    c = token[1]
                    for k in range(text_idx, len(text) + 1):
                        # Check how many consecutive c's we can match starting at text_idx
                        end = text_idx
                        while end < len(text) and text[end] == c:
                            end += 1
                        # Now check all possibilities from 1 to (end - text_idx)
                        for j in range(text_idx + 1, min(end + 1, k + 1)):
                            if match_tokens(tokens_idx + 1, j):
                                return True
                else:  # quant_class
                    chars, negated = token[1], token[2]
                    for k in range(text_idx, len(text) + 1):
                        end = text_idx
                        while end < len(text):
                            char_in_set = (text[end] in chars) if not negated else (text[end] not in chars)
                            if char_in_set:
                                end += 1
                            else:
                                break
                        # Try all possibilities from 1 to (end - text_idx)
                        for j in range(text_idx + 1, min(end + 1, k + 1)):
                            if match_tokens(tokens_idx + 1, j):
                                return True
                
                return False
                
            elif quantifier == '+':  # One or more
                matched = False
                if token[0] == 'quant_any':
                    for k in range(text_idx + 1, len(text) + 1):
                        if match_tokens(tokens_idx + 1, k):
                            matched = True
                            break
                elif token[0] == 'quant_literal':
                    c = token[1]
                    end = text_idx
                    while end < len(text) and text[end] == c:
                        end += 1
                    for j in range(text_idx + 1, end + 1):
                        if match_tokens(tokens_idx + 1, j):
                            matched = True
                            break
                else:  # quant_class
                    chars, negated = token[1], token[2]
                    end = text_idx
                    while end < len(text):
                        char_in_set = (text[end] in chars) if not negated else (text[end] not in chars)
                        if char_in_set:
                            end += 1
                        else:
                            break
                    for j in range(text_idx + 1, end + 1):
                        if match_tokens(tokens_idx + 1, j):
                            matched = True
                            break
                
                return matched
                
            else:  # quantifier == '?'
                # Zero or one occurrence
                if match_tokens(tokens_idx + 1, text_idx):
                    return True
                
                # One occurrence
                if token[0] == 'quant_any':
                    if text_idx < len(text) and match_tokens(tokens_idx + 1, text_idx + 1):
                        return True
                elif token[0] == 'quant_literal':
                    c = token[1]
                    if text_idx < len(text) and text[text_idx] == c and match_tokens(tokens_idx + 1, text_idx + 1):
                        return True
                else:  # quant_class
                    chars, negated = token[1], token[2]
                    if text_idx < len(text):
                        char_in_set = (text[text_idx] in chars) if not negated else (text[text_idx] not in chars)
                        if char_in_set and match_tokens(tokens_idx + 1, text_idx + 1):
                            return True
                
                return False
        
        # Handle tokens without quantifiers
        else:
            if token[0] == 'any':  # '.' matches any single character
                if text_idx < len(text) and match_tokens(tokens_idx + 1, text_idx + 1):
                    return True
                return False
            
            elif token[0] == 'literal':
                c = token[1]
                if text_idx < len(text) and text[text_idx] == c and match_tokens(tokens_idx + 1, text_idx + 1):
                    return True
                return False
            
            else:  # class
                chars, negated = token[1], token[2]
                if text_idx < len(text):
                    char_in_set = (text[text_idx] in chars) if not negated else (text[text_idx] not in chars)
                    if char_in_set and match_tokens(tokens_idx + 1, text_idx + 1):
                        return True
                return False
    
    return match_tokens(0, 0)
