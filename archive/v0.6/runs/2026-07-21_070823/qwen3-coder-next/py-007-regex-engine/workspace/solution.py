def match(pattern: str, text: str) -> bool:
    """
    Match pattern against entire text using recursive backtracking.
    
    Supports:
    - literal characters
    - '.' (any single character)
    - '*' (zero or more of preceding element)
    - '+' (one or more of preceding element)
    - '?' (zero or one of preceding element)
    - character classes [abc], ranges [a-z0-9], negation [^abc]
    """
    if not pattern:
        return text == ""
    
    # Parse the pattern and check for malformed patterns
    try:
        parsed = _parse_pattern(pattern)
    except ValueError as e:
        raise e
    
    # Use memoization to avoid exponential time on overlapping subproblems
    memo = {}
    
    def _match_recursive(p_idx, t_idx):
        """
        Match parsed pattern from p_idx against text from t_idx.
        Returns True if match is successful.
        """
        if (p_idx, t_idx) in memo:
            return memo[(p_idx, t_idx)]
        
        # Base case: pattern exhausted
        if p_idx == len(parsed):
            result = t_idx == len(text)
            memo[(p_idx, t_idx)] = result
            return result
        
        current_token = parsed[p_idx]
        
        # If text is exhausted but pattern isn't
        if t_idx == len(text):
            # Only match if remaining tokens can match empty string (i.e., are quantifiers with zero matches)
            for i in range(p_idx, len(parsed)):
                token = parsed[i]
                if not _can_match_empty(token):
                    memo[(p_idx, t_idx)] = False
                    return False
            memo[(p_idx, t_idx)] = True
            return True
        
        # Process current token and possible quantifiers
        result = False
        
        if isinstance(current_token, str) or isinstance(current_token, tuple):
            # Handle literal, '.', or character class
            
            # Check if next token is a quantifier
            if p_idx + 1 < len(parsed) and isinstance(parsed[p_idx+1], str) and parsed[p_idx+1] in '*+?':
                quantifier = parsed[p_idx+1]
                
                if quantifier == '*':  # zero or more
                    # Try zero occurrences first (skip token)
                    result = _match_recursive(p_idx + 2, t_idx)
                    
                    # If that didn't work, try matching one and recurse
                    if not result:
                        if _matches_char(current_token, text[t_idx]):
                            result = _match_recursive(p_idx, t_idx + 1) or _match_recursive(p_idx + 2, t_idx)
                
                elif quantifier == '+':  # one or more
                    if _matches_char(current_token, text[t_idx]):
                        # Try matching one and continue with same token (for more matches)
                        result = _match_recursive(p_idx + 1, t_idx + 1) or _match_recursive(p_idx, t_idx + 1)
                
                elif quantifier == '?':  # zero or one
                    # Try zero occurrences first
                    result = _match_recursive(p_idx + 2, t_idx)
                    
                    # If that didn't work, try matching one
                    if not result and _matches_char(current_token, text[t_idx]):
                        result = _match_recursive(p_idx + 2, t_idx + 1)
            
            else:
                # No quantifier - must match exactly once
                if _matches_char(current_token, text[t_idx]):
                    result = _match_recursive(p_idx + 1, t_idx + 1)
        
        memo[(p_idx, t_idx)] = result
        return result
    
    return _match_recursive(0, 0)


def _parse_pattern(pattern: str):
    """Parse pattern into tokens and validate structure."""
    if not pattern:
        return []
    
    tokens = []
    i = 0
    n = len(pattern)
    
    while i < n:
        c = pattern[i]
        
        if c == '[':
            # Parse character class
            j = i + 1
            negated = False
            
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            
            if j >= n:
                raise ValueError("Unclosed character class")
            
            # Find closing bracket
            close_idx = j
            while close_idx < n and pattern[close_idx] != ']':
                close_idx += 1
            
            if close_idx >= n:
                raise ValueError("Unclosed character class")
            
            char_class_str = pattern[i+1:close_idx]
            if len(char_class_str) == 0:
                raise ValueError("Empty character class")
            
            # Parse the character class content
            char_set = set()
            k = 0
            while k < len(char_class_str):
                if k + 2 < len(char_class_str) and char_class_str[k+1] == '-' and (k+2 >= len(char_class_str) or char_class_str[k+2] != ']'):
                    # Range like a-z
                    start_char = char_class_str[k]
                    end_char = char_class_str[k+2]
                    
                    if ord(start_char) > ord(end_char):
                        raise ValueError(f"Invalid character range: {start_char}-{end_char}")
                    
                    for code in range(ord(start_char), ord(end_char)+1):
                        char_set.add(chr(code))
                    k += 3
                else:
                    # Single character
                    char_set.add(char_class_str[k])
                    k += 1
            
            tokens.append(('class', char_set, negated))
            i = close_idx + 1
        
        elif c == '.':
            tokens.append('.')
            i += 1
        
        elif c in '*+?':
            # These must follow a token
            if not tokens:
                raise ValueError(f"'{c}' cannot be at the start of pattern")
            
            last_token = tokens[-1]
            if isinstance(last_token, str) and last_token in '*+?':
                raise ValueError(f"Consecutive quantifiers: {last_token}{c}")
            
            # Check that current token can have a quantifier
            if not (isinstance(last_token, str) or 
                    isinstance(last_token, tuple) and (last_token[0] == 'class')):
                raise ValueError(f"'{c}' must follow a character or class")
            
            tokens.append(c)
            i += 1
        
        else:
            # Regular literal character
            tokens.append(c)
            i += 1
    
    return tokens


def _matches_char(token, char):
    """Check if token matches a single character."""
    if isinstance(token, str):
        if token == '.':
            return True
        else:
            return token == char
    elif isinstance(token, tuple) and token[0] == 'class':
        char_set, negated = token[1], token[2]
        in_class = char in char_set
        return not in_class if negated else in_class
    return False


def _can_match_empty(token):
    """Check if a token can match an empty string (i.e., zero occurrences)."""
    # Only quantifiers with * can match empty strings
    if isinstance(token, str) and token == '*':
        return True
    
    # A single character or class cannot match empty string
    return False
