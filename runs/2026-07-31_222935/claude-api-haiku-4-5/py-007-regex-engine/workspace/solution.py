def match(pattern: str, text: str) -> bool:
    """
    Match a pattern against text using recursive backtracking.
    Returns True if the pattern matches the entire text.
    """
    
    def parse_char_class(pattern: str, idx: int) -> tuple[callable, int]:
        """Parse a character class and return a matcher function and next index."""
        if idx >= len(pattern) or pattern[idx] != '[':
            raise ValueError("Expected '['")
        
        idx += 1
        if idx >= len(pattern):
            raise ValueError("Unclosed character class")
        
        negate = False
        if pattern[idx] == '^':
            negate = True
            idx += 1
        
        if idx >= len(pattern):
            raise ValueError("Unclosed character class")
        
        ranges = []
        while idx < len(pattern) and pattern[idx] != ']':
            if pattern[idx] == '-' and ranges and idx + 1 < len(pattern) and pattern[idx + 1] != ']':
                # This is a range
                start = ranges.pop()
                idx += 1
                end = pattern[idx]
                ranges.append((start, end))
                idx += 1
            else:
                ranges.append(pattern[idx])
                idx += 1
        
        if idx >= len(pattern):
            raise ValueError("Unclosed character class")
        
        idx += 1  # Skip ']'
        
        def char_matcher(ch: str) -> bool:
            matched = False
            for r in ranges:
                if isinstance(r, tuple):
                    start, end = r
                    if ord(start) <= ord(ch) <= ord(end):
                        matched = True
                        break
                else:
                    if ch == r:
                        matched = True
                        break
            return matched != negate
        
        return char_matcher, idx
    
    def parse_pattern(pattern: str) -> list:
        """Parse pattern into tokens: (type, value)."""
        tokens = []
        idx = 0
        
        while idx < len(pattern):
            if pattern[idx] == '[':
                matcher, idx = parse_char_class(pattern, idx)
                tokens.append(('class', matcher))
            elif pattern[idx] == '.':
                tokens.append(('dot', None))
                idx += 1
            elif pattern[idx] == '*':
                raise ValueError("Nothing to repeat for '*'")
            elif pattern[idx] == '+':
                raise ValueError("Nothing to repeat for '+'")
            elif pattern[idx] == '?':
                raise ValueError("Nothing to repeat for '?'")
            else:
                tokens.append(('char', pattern[idx]))
                idx += 1
            
            # Check for quantifiers
            if idx < len(pattern) and pattern[idx] in '*+?':
                quantifier = pattern[idx]
                tokens.append(('quantifier', quantifier))
                idx += 1
        
        return tokens
    
    def backtrack(tokens: list, token_idx: int, text: str, text_idx: int) -> bool:
        """Recursively match tokens against text."""
        # Base case: all tokens consumed
        if token_idx >= len(tokens):
            return text_idx == len(text)
        
        token_type, token_value = tokens[token_idx]
        
        # Check if next token is a quantifier
        has_quantifier = (token_idx + 1 < len(tokens) and 
                         tokens[token_idx + 1][0] == 'quantifier')
        
        if has_quantifier:
            quantifier = tokens[token_idx + 1][1]
            next_token_idx = token_idx + 2
            
            if quantifier == '*':
                # Zero or more: try matching 0, 1, 2, ... times
                if backtrack(tokens, next_token_idx, text, text_idx):
                    return True
                match_count = 0
                while text_idx + match_count < len(text):
                    if token_type == 'dot':
                        match_count += 1
                    elif token_type == 'char':
                        if text[text_idx + match_count] == token_value:
                            match_count += 1
                        else:
                            break
                    elif token_type == 'class':
                        if token_value(text[text_idx + match_count]):
                            match_count += 1
                        else:
                            break
                    
                    if backtrack(tokens, next_token_idx, text, text_idx + match_count):
                        return True
                return False
            
            elif quantifier == '+':
                # One or more: must match at least once
                match_count = 0
                while text_idx + match_count < len(text):
                    if token_type == 'dot':
                        match_count += 1
                    elif token_type == 'char':
                        if text[text_idx + match_count] == token_value:
                            match_count += 1
                        else:
                            break
                    elif token_type == 'class':
                        if token_value(text[text_idx + match_count]):
                            match_count += 1
                        else:
                            break
                    
                    if match_count > 0 and backtrack(tokens, next_token_idx, text, text_idx + match_count):
                        return True
                return False
            
            elif quantifier == '?':
                # Zero or one
                if backtrack(tokens, next_token_idx, text, text_idx):
                    return True
                if text_idx < len(text):
                    if token_type == 'dot':
                        return backtrack(tokens, next_token_idx, text, text_idx + 1)
                    elif token_type == 'char':
                        if text[text_idx] == token_value:
                            return backtrack(tokens, next_token_idx, text, text_idx + 1)
                    elif token_type == 'class':
                        if token_value(text[text_idx]):
                            return backtrack(tokens, next_token_idx, text, text_idx + 1)
                return False
        else:
            # No quantifier, must match exactly one character
            if text_idx >= len(text):
                return False
            
            if token_type == 'dot':
                return backtrack(tokens, token_idx + 1, text, text_idx + 1)
            elif token_type == 'char':
                if text[text_idx] == token_value:
                    return backtrack(tokens, token_idx + 1, text, text_idx + 1)
                return False
            elif token_type == 'class':
                if token_value(text[text_idx]):
                    return backtrack(tokens, token_idx + 1, text, text_idx + 1)
                return False
            
            return False
    
    tokens = parse_pattern(pattern)
    return backtrack(tokens, 0, text, 0)
