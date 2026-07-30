def match(pattern: str, text: str) -> bool:
    """Match pattern against the entire text."""
    _validate_pattern(pattern)
    return _match_recursive(pattern, 0, text, 0)


def _validate_pattern(pattern):
    """Validate that the pattern is well-formed."""
    i = 0
    
    while i < len(pattern):
        c = pattern[i]
        
        if c == '[':
            j = i + 1
            if j >= len(pattern):
                raise ValueError("Unclosed '['")
            
            if pattern[j] == '^':
                j += 1
                if j >= len(pattern):
                    raise ValueError("Unclosed '['")
            
            if j < len(pattern) and pattern[j] == ']':
                j += 1
            
            while j < len(pattern) and pattern[j] != ']':
                j += 1
            
            if j >= len(pattern):
                raise ValueError("Unclosed '['")
            
            i = j + 1
        
        elif c in '*+?':
            if i == 0:
                raise ValueError("Nothing to repeat")
            if pattern[i - 1] in '*+?':
                raise ValueError("Nothing to repeat")
            i += 1
        
        elif c == ']':
            raise ValueError("Unmatched ']'")
        
        else:
            i += 1


def _match_recursive(pattern, p, text, t):
    """Recursively match pattern[p:] against text[t:]."""
    if p == len(pattern):
        return t == len(text)
    
    has_quantifier = p + 1 < len(pattern) and pattern[p + 1] in '*+?'
    
    if has_quantifier:
        quantifier = pattern[p + 1]
        
        if quantifier == '*':
            if _match_recursive(pattern, p + 2, text, t):
                return True
            if t < len(text) and _matches_element(pattern, p, text, t):
                return _match_recursive(pattern, p, text, t + 1)
            return False
        
        elif quantifier == '+':
            if t >= len(text) or not _matches_element(pattern, p, text, t):
                return False
            if _match_recursive(pattern, p, text, t + 1):
                return True
            if _match_recursive(pattern, p + 2, text, t + 1):
                return True
            return False
        
        elif quantifier == '?':
            if _match_recursive(pattern, p + 2, text, t):
                return True
            if t < len(text) and _matches_element(pattern, p, text, t):
                return _match_recursive(pattern, p + 2, text, t + 1)
            return False
    
    else:
        if t >= len(text) or not _matches_element(pattern, p, text, t):
            return False
        return _match_recursive(pattern, p + 1, text, t + 1)


def _matches_element(pattern, p, text, t):
    """Check if pattern[p] matches text[t]."""
    if p >= len(pattern) or t >= len(text):
        return False
    
    if pattern[p] == '.':
        return True
    elif pattern[p] == '[':
        _, is_negated, class_content = _parse_char_class(pattern, p)
        return _char_matches_class(text[t], class_content, is_negated)
    else:
        return pattern[p] == text[t]


def _parse_char_class(pattern, start_idx):
    """Parse a character class starting at start_idx."""
    if start_idx >= len(pattern) or pattern[start_idx] != '[':
        raise ValueError("Expected '['")
    
    i = start_idx + 1
    if i >= len(pattern):
        raise ValueError("Unclosed '['")
    
    is_negated = False
    if pattern[i] == '^':
        is_negated = True
        i += 1
        if i >= len(pattern):
            raise ValueError("Unclosed '['")
    
    start_content = i
    
    if i < len(pattern) and pattern[i] == ']':
        i += 1
    
    while i < len(pattern) and pattern[i] != ']':
        i += 1
    
    if i >= len(pattern):
        raise ValueError("Unclosed '['")
    
    class_content = pattern[start_content:i]
    return i + 1, is_negated, class_content


def _char_matches_class(char, class_content, is_negated):
    """Check if char matches the character class."""
    matches = False
    i = 0
    
    while i < len(class_content):
        if i + 2 < len(class_content) and class_content[i + 1] == '-':
            start_char = class_content[i]
            end_char = class_content[i + 2]
            if start_char <= char <= end_char:
                matches = True
            i += 3
        else:
            if class_content[i] == char:
                matches = True
            i += 1
    
    if is_negated:
        matches = not matches
    
    return matches
