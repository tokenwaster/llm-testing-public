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
    
    # Use memoization to avoid recomputing states
    memo = {}
    
    def _match_recursive(p_idx, t_idx):
        """
        Returns True if pattern[p_idx:] matches text[t_idx:].
        p_idx is an index into the parsed pattern list.
        """
        if (p_idx, t_idx) in memo:
            return memo[(p_idx, t_idx)]
        
        # If we've consumed all pattern elements
        if p_idx == len(parsed):
            result = t_idx == len(text)
            memo[(p_idx, t_idx)] = result
            return result
        
        current_pattern = parsed[p_idx]
        
        # Handle quantifiers that apply to the previous element
        # But in our parsed format, each pattern element includes its quantifier
        # So we handle them directly here
        
        if t_idx == len(text):
            # If text is exhausted, only match if remaining pattern can match empty string
            # This happens when all remaining elements are optional (zero occurrences)
            result = _can_match_empty(parsed[p_idx:])
            memo[(p_idx, t_idx)] = result
            return result
        
        p_type, p_value, quantifier = current_pattern
        
        # Try matching the current pattern element against text[t_idx]
        matched_char = False
        if p_type == 'literal':
            matched_char = (text[t_idx] == p_value)
        elif p_type == 'dot':
            matched_char = True  # '.' matches any single character
        elif p_type == 'class':
            char = text[t_idx]
            if p_value[0]:  # negation flag
                # Check if char is NOT in the class
                matched_char = not _char_in_class(char, p_value[1])
            else:
                matched_char = _char_in_class(char, p_value[1])
        
        result = False
        
        if quantifier == '*':
            # Zero or more: try zero occurrences first (skip this pattern element)
            if _match_recursive(p_idx + 1, t_idx):
                result = True
            # Or match one and continue with same pattern element
            elif matched_char and _match_recursive(p_idx, t_idx + 1):
                result = True
        elif quantifier == '+':
            # One or more: must match at least once
            if matched_char:
                # Try matching one and move to next pattern element
                if _match_recursive(p_idx + 1, t_idx + 1):
                    result = True
                # Or match one and continue with same pattern element (for more matches)
                elif _match_recursive(p_idx, t_idx + 1):
                    result = True
        elif quantifier == '?':
            # Zero or one: try zero occurrences first
            if _match_recursive(p_idx + 1, t_idx):
                result = True
            # Or match one occurrence
            elif matched_char and _match_recursive(p_idx + 1, t_idx + 1):
                result = True
        else:  # no quantifier (implicit once)
            if matched_char:
                result = _match_recursive(p_idx + 1, t_idx + 1)
        
        memo[(p_idx, t_idx)] = result
        return result
    
    return _match_recursive(0, 0)


def _char_in_class(char, class_ranges):
    """Check if char is in the class defined by ranges."""
    for start, end in class_ranges:
        if ord(start) <= ord(char) <= ord(end):
            return True
    return False


def _can_match_empty(pattern_list):
    """Check if pattern can match an empty string (all remaining elements are optional)."""
    for p_type, p_value, quantifier in pattern_list:
        # Only * and ? allow zero occurrences; + requires at least one
        if quantifier == '+':
            return False
        # For literal, dot, class without quantifier, they must match something
        if quantifier is None:
            return False
    return True


def _parse_pattern(pattern):
    """Parse pattern string into a list of (type, value, quantifier) tuples."""
    if not pattern:
        return []
    
    result = []
    i = 0
    
    while i < len(pattern):
        c = pattern[i]
        
        # Check for special characters that start character classes
        if c == '[':
            # Find closing bracket
            j = i + 1
            negated = False
            
            # Handle negation
            if j < len(pattern) and pattern[j] == '^':
                negated = True
                j += 1
            
            # Find the end of the character class
            while j < len(pattern) and pattern[j] != ']':
                j += 1
            
            if j >= len(pattern):
                raise ValueError("Unclosed character class")
            
            # Parse the content between [ and ]
            class_content = pattern[i+1:j]
            if negated:
                class_content = class_content[1:]  # Remove leading ^
            
            # Validate that there's at least one character in the class
            if not class_content and not negated:
                raise ValueError("Empty character class")
            
            # Parse ranges and individual characters
            ranges = []
            k = 0
            while k < len(class_content):
                # Check for range (a-z)
                if k + 2 < len(class_content) and class_content[k+1] == '-':
                    start_char = class_content[k]
                    end_char = class_content[k+2]
                    
                    # Validate range
                    if ord(start_char) > ord(end_char):
                        raise ValueError(f"Invalid character range: {start_char}-{end_char}")
                    
                    ranges.append((start_char, end_char))
                    k += 3
                else:
                    # Single character
                    char = class_content[k]
                    ranges.append((char, char))
                    k += 1
            
            result.append(('class', (negated, ranges), None))
            i = j + 1
        
        elif c == '.':
            result.append(('dot', '.', None))
            i += 1
        
        elif c in '*+?':
            # These should follow a pattern element
            if not result:
                raise ValueError(f"'{c}' must follow a pattern element")
            
            # Apply quantifier to the last element
            prev_type, prev_value, _ = result[-1]
            if c == '*':
                result[-1] = (prev_type, prev_value, '*')
            elif c == '+':
                result[-1] = (prev_type, prev_value, '+')
            else:  # '?'
                result[-1] = (prev_type, prev_value, '?')
            i += 1
        
        else:
            # Literal character
            result.append(('literal', c, None))
            i += 1
    
    return result
