def match(pattern: str, text: str) -> bool:
    def parse_pattern(p):
        tokens = []
        i = 0
        while i < len(p):
            if p[i] == '[':
                j = i + 1
                if j >= len(p):
                    raise ValueError("Unclosed character class")
                
                negated = False
                if p[j] == '^':
                    negated = True
                    j += 1
                
                chars = set()
                if j < len(p) and p[j] == ']':
                    chars.add(']')
                    j += 1
                
                while j < len(p) and p[j] != ']':
                    if j + 2 < len(p) and p[j + 1] == '-' and p[j + 2] != ']':
                        start_char, end_char = p[j], p[j + 2]
                        if start_char > end_char:
                            raise ValueError("Invalid range")
                        for c in range(ord(start_char), ord(end_char) + 1):
                            chars.add(chr(c))
                        j += 3
                    else:
                        chars.add(p[j])
                        j += 1
                
                if j >= len(p):
                    raise ValueError("Unclosed character class")
                
                j += 1
                char_class = (negated, chars)
                
                quantifier = None
                if j < len(p) and p[j] in '*+?':
                    quantifier = p[j]
                    j += 1
                
                tokens.append((char_class, quantifier))
                i = j
            
            elif p[i] in '*+?':
                raise ValueError("Quantifier has nothing to apply to")
            
            elif p[i] == ']':
                raise ValueError("Unexpected ]")
            
            else:
                element = p[i]
                i += 1
                
                quantifier = None
                if i < len(p) and p[i] in '*+?':
                    quantifier = p[i]
                    i += 1
                
                tokens.append((element, quantifier))
        
        return tokens
    
    def matches_element(element, char):
        if isinstance(element, str):
            return element == '.' or element == char
        else:
            negated, chars = element
            result = char in chars
            return (not result) if negated else result
    
    def helper(t_idx, token_idx):
        if token_idx == len(tokens):
            return t_idx == len(text)
        
        element, quantifier = tokens[token_idx]
        
        if quantifier is None:
            if t_idx >= len(text) or not matches_element(element, text[t_idx]):
                return False
            return helper(t_idx + 1, token_idx + 1)
        
        elif quantifier == '*':
            if helper(t_idx, token_idx + 1):
                return True
            if t_idx < len(text) and matches_element(element, text[t_idx]):
                if helper(t_idx + 1, token_idx):
                    return True
            return False
        
        elif quantifier == '+':
            if t_idx >= len(text) or not matches_element(element, text[t_idx]):
                return False
            if helper(t_idx + 1, token_idx):
                return True
            return helper(t_idx + 1, token_idx + 1)
        
        elif quantifier == '?':
            if helper(t_idx, token_idx + 1):
                return True
            if t_idx < len(text) and matches_element(element, text[t_idx]):
                if helper(t_idx + 1, token_idx + 1):
                    return True
            return False
    
    tokens = parse_pattern(pattern)
    return helper(0, 0)
