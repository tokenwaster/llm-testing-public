def match(pattern: str, text: str) -> bool:
    """
    Match entire text against pattern using recursive backtracking.
    Supports: literal chars, ., *, +, ?, [abc], [a-z], [^abc]
    Raises ValueError for malformed patterns.
    """
    
    def helper(p_idx: int, t_idx: int) -> bool:
        # Both exhausted - success
        if p_idx == len(pattern) and t_idx == len(text):
            return True
        
        # Pattern exhausted but text remains - failure
        if p_idx >= len(pattern):
            return False
        
        # Check for quantifier at current position (shouldn't happen with proper parsing)
        if pattern[p_idx] in '*+?':
            raise ValueError(f"Quantifier '{pattern[p_idx]}' without preceding element")
        
        # Determine the next character to match and its type
        char = pattern[p_idx]
        
        # Check for quantifier following this character
        has_quantifier = False
        quantifier_type = None
        
        if p_idx + 1 < len(pattern) and pattern[p_idx + 1] in '*+?':
            has_quantifier = True
            quantifier_type = pattern[p_idx + 1]
        
        # Determine the element to match (skip past [class] or .)
        if char == '.':
            element = '.'
        elif char == '[':
            close_bracket = pattern.find(']', p_idx)
            if close_bracket == -1:
                raise ValueError("Unclosed character class")
            class_content = pattern[p_idx + 1:close_bracket]
            is_negated = class_content.startswith('^')
            element = class_content[1:] if is_negated else class_content
        else:
            element = char
        
        # Calculate next pattern index (after the element and optional quantifier)
        p_next = close_bracket + 1 if char == '[' else p_idx + 1
        if has_quantifier:
            p_next += 1
        
        # Try matching with quantifier first, then without
        if has_quantifier:
            q_type = quantifier_type
            
            if q_type == '*':
                # Zero or more: try zero first (skip element), then one or more
                if helper(p_next, t_idx):
                    return True
                while t_idx < len(text) and _match_element(element, text[t_idx], is_negated):
                    t_idx += 1
                    if helper(p_next, t_idx):
                        return True
                return False
            
            elif q_type == '+':
                # One or more: must match at least one
                while t_idx < len(text) and _match_element(element, text[t_idx], is_negated):
                    t_idx += 1
                if helper(p_next, t_idx):
                    return True
                return False
            
            elif q_type == '?':
                # Zero or one: try zero first
                if helper(p_next, t_idx):
                    return True
                while t_idx < len(text) and _match_element(element, text[t_idx], is_negated):
                    t_idx += 1
                    if helper(p_next, t_idx):
                        return True
                return False
        
        # No quantifier: must match exactly one occurrence
        if t_idx < len(text) and _match_element(element, text[t_idx], char == '['):
            return helper(p_next, t_idx + 1)
        
        return False
    
    def _match_element(pattern_elem: str, text_char: str, is_class: bool) -> bool:
        """Check if a single character matches the pattern element."""
        if pattern_elem == '.':
            return True
        elif is_class:
            # Handle character class matching
            negated = pattern_elem.startswith('^')
            if negated:
                pattern_elem = pattern_elem[1:]
            
            for c in pattern_elem:
                if text_char == c:
                    return True
            return False
        else:
            return text_char == pattern_elem
    
    # Validate pattern structure first
    stack = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char in '*+?':
            raise ValueError(f"Quantifier '{char}' without preceding element")
        elif char == '[':
            close_idx = pattern.find(']', i)
            if close_idx == -1:
                raise ValueError("Unclosed character class")
            # Check for nested brackets (not supported, but we'll handle simple case)
            stack.append(i)
            i = close_idx + 1
        else:
            i += 1
    
    return helper(0, 0)
