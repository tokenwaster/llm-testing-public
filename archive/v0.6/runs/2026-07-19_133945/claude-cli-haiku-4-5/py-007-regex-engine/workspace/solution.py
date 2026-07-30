def match(pattern: str, text: str) -> bool:
    # Validate pattern
    in_class = False
    prev_was_quantifier = False
    
    for i, ch in enumerate(pattern):
        if ch == '[':
            in_class = True
            prev_was_quantifier = False
        elif ch == ']':
            in_class = False
            prev_was_quantifier = False
        elif ch in '*+?' and not in_class:
            if i == 0 or prev_was_quantifier:
                raise ValueError("Nothing to repeat")
            prev_was_quantifier = True
        else:
            prev_was_quantifier = False
    
    if in_class:
        raise ValueError("Unclosed character class")
    
    def helper(p_idx: int, t_idx: int) -> bool:
        if p_idx == len(pattern):
            return t_idx == len(text)
        
        # Parse element (character or character class)
        if pattern[p_idx] == '[':
            end = p_idx + 1
            if end < len(pattern) and pattern[end] == '^':
                end += 1
            while end < len(pattern) and pattern[end] != ']':
                end += 1
            element = pattern[p_idx:end+1]
            element_len = end + 1 - p_idx
        else:
            element = pattern[p_idx]
            element_len = 1
        
        next_p_idx = p_idx + element_len
        
        # Check for quantifier
        if next_p_idx < len(pattern) and pattern[next_p_idx] in '*+?':
            quantifier = pattern[next_p_idx]
            next_p_idx += 1
            
            if quantifier == '*':
                # Try 0 matches first
                if helper(next_p_idx, t_idx):
                    return True
                # Try 1+ matches (greedy with backtracking)
                count = 0
                for i in range(t_idx, len(text)):
                    if element_matches(element, i):
                        count += 1
                    else:
                        break
                for c in range(count, 0, -1):
                    if helper(next_p_idx, t_idx + c):
                        return True
                return False
            elif quantifier == '+':
                # Must match at least once
                count = 0
                for i in range(t_idx, len(text)):
                    if element_matches(element, i):
                        count += 1
                    else:
                        break
                if count == 0:
                    return False
                for c in range(count, 0, -1):
                    if helper(next_p_idx, t_idx + c):
                        return True
                return False
            elif quantifier == '?':
                # Try 0 matches
                if helper(next_p_idx, t_idx):
                    return True
                # Try 1 match
                if t_idx < len(text) and element_matches(element, t_idx):
                    if helper(next_p_idx, t_idx + 1):
                        return True
                return False
        else:
            # No quantifier, must match exactly once
            if t_idx < len(text) and element_matches(element, t_idx):
                return helper(next_p_idx, t_idx + 1)
            return False
    
    def element_matches(element: str, text_idx: int) -> bool:
        if text_idx >= len(text):
            return False
        if element == '.':
            return True
        elif element.startswith('['):
            return match_class(element, text[text_idx])
        else:
            return element == text[text_idx]
    
    def match_class(class_str: str, char: str) -> bool:
        content = class_str[1:-1]  # Remove [ and ]
        negated = len(content) > 0 and content[0] == '^'
        if negated:
            content = content[1:]
        
        matched = False
        i = 0
        while i < len(content):
            if i + 1 < len(content) and content[i + 1] == '-' and i + 2 < len(content):
                # This is a range
                start = content[i]
                end = content[i + 2]
                if start <= char <= end:
                    matched = True
                    break
                i += 3
            else:
                # Single character
                if content[i] == char:
                    matched = True
                    break
                i += 1
        
        return matched if not negated else not matched
    
    return helper(0, 0)
