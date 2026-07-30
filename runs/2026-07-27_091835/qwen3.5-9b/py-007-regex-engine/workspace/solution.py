def match(pattern: str, text: str) -> bool:
    """Match entire text against regex pattern without using re module."""
    
    def _is_in_class(char: str, class_pattern: str, negated: bool = False) -> bool:
        """Check if char matches a character class"""
        pos = 0
        while pos < len(class_pattern):
            c = class_pattern[pos]
            
            # Handle escaped characters
            if c == '\\' and pos + 1 < len(class_pattern):
                actual = class_pattern[pos + 1]
                if ord(actual) != ord('\\'):
                    return char == actual
                pos += 2
                continue
            
            # Check for ranges like a-z or A-Z
            if c.isalnum() and pos + 1 < len(class_pattern) and class_pattern[pos + 1] == '-':
                if pos + 2 < len(class_pattern):
                    end = class_pattern[pos + 2]
                    for r in range(ord(c), ord(end) + 1):
                        if char == chr(r):
                            return True
                    return False
                pos += 2
            elif c != '-':
                # Regular character match
                return char == c
            pos += 1
        
        return False
    
    def _match(p_idx: int, t_idx: int) -> bool:
        """Recursive backtracking matcher"""
        # Both exhausted - successful match
        if p_idx >= len(pattern) and t_idx >= len(text):
            return True
        
        # Text exhausted - check if remaining pattern can be skipped
        if t_idx >= len(text):
            while p_idx < len(pattern) and pattern[p_idx] == '*':
                p_idx += 1
            return p_idx >= len(pattern)
        
        # Pattern exhausted but text remains - no match
        if p_idx >= len(pattern):
            return False
        
        char = pattern[p_idx]
        
        # Handle character class [...]
        if char == '[':
            # Find closing ]
            j = p_idx + 1
            while j < len(pattern):
                if pattern[j] == '\\' and j + 1 < len(pattern):
                    j += 2
                elif pattern[j] != ']':
                    j += 1
            
            close_bracket = j
            class_content = pattern[p_idx+1:close_bracket]
            
            # Parse character class content
            is_negated = False
            pos = 0
            while pos < len(class_content):
                c = class_content[pos]
                
                if c == '^' and not is_negated:
                    is_negated = True
                    pos += 1
                elif c == '\\':
                    pos += 2
                else:
                    break
            
            close_pos = p_idx + close_bracket - p_idx + 1
            
            # Consume matching characters from text
            while t_idx < len(text):
                if not _is_in_class(text[t_idx], class_content, is_negated):
                    break
                t_idx += 1
            
            return _match(close_pos + 1, t_idx)
        
        # Handle . wildcard
        if char == '.':
            return _match(p_idx + 1, t_idx + 1)
        
        # Regular literal character match (not at quantifier position)
        is_quantifier_start = p_idx < len(pattern) - 1 and pattern[p_idx] in '*+?'
        is_after_class = p_idx > 0
        
        if char == '*' or char == '+' or char == '?':
            raise ValueError("Quantifier without preceding element")
        
        # Look ahead to detect quantifiers on next character
        next_char = ''
        for i in range(p_idx + 1, len(pattern)):
            c = pattern[i]
            if c in '*+?[]\\':
                break
            next_char = c
        
        # If next char is a quantifier, handle it
        if p_idx + 1 < len(pattern):
            next_pos = p_idx + 1
            next_c = pattern[next_pos]
            
            if next_c == '*':
                return _match_star(p_idx, t_idx)
            elif next_c == '+':
                return _match_plus(p_idx, t_idx)
            elif next_c == '?':
                return _match_question(p_idx, t_idx)
        
        # Single character match without quantifier
        if char != text[t_idx]:
            return False
        
        return _match(p_idx + 1, t_idx + 1)
    
    def _match_star(p_idx: int, t_idx: int) -> bool:
        """Handle * quantifier"""
        elem = pattern[p_idx]
        
        # Try matching zero times (skip *)
        if _match(p_idx + 2, t_idx):
            return True
        
        # Try matching one or more
        while t_idx < len(text) and (elem == '.' or text[t_idx] == elem):
            t_idx += 1
        
        return _match(p_idx + 2, t_idx)
    
    def _match_plus(p_idx: int, t_idx: int) -> bool:
        """Handle + quantifier"""
        elem = pattern[p_idx]
        
        # Must match at least one
        while t_idx < len(text) and (elem == '.' or text[t_idx] == elem):
            t_idx += 1
        
        if t_idx >= len(text):
            return False
        
        return _match(p_idx + 2, t_idx)
    
    def _match_question(p_idx: int, t_idx: int) -> bool:
        """Handle ? quantifier"""
        elem = pattern[p_idx]
        
        # Try matching zero times first
        if _match(p_idx + 2, t_idx):
            return True
        
        # Try matching one time
        while t_idx < len(text) and (elem == '.' or text[t_idx] == elem):
            t_idx += 1
        
        return _match(p_idx + 2, t_idx)
    
    def _validate_pattern() -> bool:
        """Validate pattern for malformed constructs"""
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            if char == '[':
                # Find closing ]
                j = i + 1
                while j < len(pattern) and pattern[j] != ']':
                    if pattern[j] == '\\' and j + 1 < len(pattern):
                        j += 2
                    else:
                        j += 1
                
                if j >= len(pattern):
                    raise ValueError("Unclosed character class")
                
                i = j + 1
            
            elif char in '*+?':
                # Check if there's a valid preceding element
                if _is_quantifier_at_position(i - 1):
                    raise ValueError("Quantifier without preceding element")
            
            i += 1
    
    def _is_quantifier_at_position(pos: int) -> bool:
        """Check if position has *+?"""
        return pos >= 0 and pattern[pos] in '*+?'
    
    # Validate then match
    _validate_pattern()
    result = _match(0, 0)
    return result


def match(pattern: str, text: str) -> bool:
    """
    Match entire text against regex pattern.
    Supports: literal chars, ., *, +, ?, [abc], ranges, negation.
    
    Args:
        pattern: The regex pattern to match against
        text: The text to check
    
    Returns:
        True if entire text matches the pattern, False otherwise
    
    Raises:
        ValueError: If the pattern is malformed (e.g., unclosed [, 
                   or *+/? without preceding element)
    """
    
    def _match(p_idx: int, t_idx: int) -> bool:
        """Main recursive matcher with backtracking"""
        
        # Base case: both consumed = match!
        if p_idx >= len(pattern) and t_idx >= len(text):
            return True
        
        # Text exhausted - check if rest of pattern is optional (* only)
        if t_idx >= len(text):
            while p_idx < len(pattern) and pattern[p_idx] == '*':
                p_idx += 1
            return p_idx >= len(pattern)
        
        # Pattern exhausted but text remains = no match
        if p_idx >= len(pattern):
            return False
        
        char = pattern[p_idx]
        
        # Validate quantifiers (shouldn't appear at pattern start)
        if char in '*+?':
            raise ValueError("Quantifier without preceding element")
        
        # Handle character class [...]
        if char == '[':
            # Find the closing ]
            j = p_idx + 1
            while j < len(pattern):
                if pattern[j] == '\\' and j + 1 < len(pattern):
                    j += 2
                elif pattern[j] != ']':
                    j += 1
            
            close_bracket = j
            if close_bracket >= len(pattern) or pattern[close_bracket] != ']':
                raise ValueError("Unclosed character class")
            
            # Parse the character class content
            class_str = pattern[p_idx + 1:close_bracket]
            
            # Check for negation
            is_negated = False
            k = 0
            while k < len(class_str):
                c = class_str[k]
                if c == '^' and not is_negated:
                    is_negated = True
                    k += 1
                elif c == '\\' and k + 1 < len(class_str):
                    k += 2
                else:
                    break
            
            # Parse characters in the class (including ranges)
            chars_in_class = set()
            pos = 0
            while pos < len(class_str):
                c = class_str[pos]
                
                # Handle escaped characters
                if c == '\\' and pos + 1 < len(class_str):
                    next_c = class_str[pos + 1]
                    if next_c != '\\':
                        chars_in_class.add(next_c)
                    pos += 2
                    continue
                
                # Handle ranges like a-z
                if c.isalnum() and pos + 1 < len(class_str) and class_str[pos + 1] == '-':
                    start = ord(c)
                    end = ord(class_str[pos + 2])
                    for r in range(start, end + 1):
                        chars_in_class.add(chr(r))
                    pos += 3
                    continue
                
                if c != '-':
                    chars_in_class.add(c)
                    pos += 1
            
            # Match text against the character class
            while t_idx < len(text):
                if is_negated:
                    if text[t_idx] not in chars_in_class:
                        t_idx += 1
                    else:
                        break
                else:
                    if text[t_idx] in chars_in_class:
                        t_idx += 1
                    else:
                        break
            
            return _match(close_bracket + 1, t_idx)
        
        # Handle . wildcard
        if char == '.':
            return _match(p_idx + 1, t_idx + 1)
        
        # Detect and handle quantifiers (*+?)
        next_pos = p_idx + 1
        while next_pos < len(pattern):
            c = pattern[next_pos]
            if c in '*+?[]\\':
                break
            next_pos += 1
        
        # Check for quantifier
        if next_pos < len(pattern) and pattern[next_pos] in '*+?':
            q_char = pattern[next_pos]
            elem = pattern[p_idx]
            
            if q_char == '*':
                return _match_star(p_idx, t_idx, elem)
            elif q_char == '+':
                return _match_plus(p_idx, t_idx, elem)
            elif q_char == '?':
                return _match_question(p_idx, t_idx, elem)
        
        # Single character match (no quantifier)
        if char != text[t_idx]:
            return False
        
        return _match(p_idx + 1, t_idx + 1)
    
    def _can_match(elem: str, char: str) -> bool:
        """Check if char matches element"""
        if elem == '.':
            return True
        return char == elem
    
    def _match_star(p_idx: int, t_idx: int, elem: str) -> bool:
        """Match * quantifier: zero or more of preceding element"""
        
        # Try matching zero times
        if _match(p_idx + 2, t_idx):
            return True
        
        # Try matching one or more
        while t_idx < len(text) and _can_match(elem, text[t_idx]):
            t_idx += 1
        
        return _match(p_idx + 2, t_idx)
    
    def _match_plus(p_idx: int, t_idx: int, elem: str) -> bool:
        """Match + quantifier: one or more of preceding element"""
        
        # Must match at least one
        while t_idx < len(text) and _can_match(elem, text[t_idx]):
            t_idx += 1
        
        if t_idx >= len(text):
            return False
        
        return _match(p_idx + 2, t_idx)
    
    def _match_question(p_idx: int, t_idx: int, elem: str) -> bool:
        """Match ? quantifier: zero or one of preceding element"""
        
        # Try matching zero times first (optional behavior)
        if _match(p_idx + 2, t_idx):
            return True
        
        # Try matching one time
        while t_idx < len(text) and _can_match(elem, text[t_idx]):
            t_idx += 1
        
        return _match(p_idx + 2, t_idx)
    
    def _validate_pattern() -> None:
        """Validate pattern for malformed constructs"""
        
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            if char == '[':
                # Find closing ]
                j = i + 1
                while j < len(pattern) and pattern[j] != ']':
                    if pattern[j] == '\\' and j + 1 < len(pattern):
                        j += 2
                    else:
                        j += 1
                
                if j >= len(pattern):
                    raise ValueError("Unclosed character class")
                
                i = j + 1
            
            elif char in '*+?':
                # Check for preceding non-quantifier element
                has_preceding = False
                for k in range(i - 1, -1, -1):
                    if pattern[k] == '*' or pattern[k] == '+' or pattern[k] == '?':
                        break
                    if pattern[k] != ']':  # Exclude character class brackets
                        has_preceding = True
                        break
                
                if not has_preceding:
                    raise ValueError("Quantifier without preceding element")
            
            i += 1
    
    # Validate then match
    _validate_pattern()
    result = _match(0, 0)
    return result
