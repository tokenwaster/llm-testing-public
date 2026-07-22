def match(pattern: str, text: str) -> bool:
    def parse_char_class(class_str):
        negated = False
        if class_str and class_str[0] == '^':
            negated = True
            class_str = class_str[1:]
        
        allowed = set()
        i = 0
        while i < len(class_str):
            if i + 2 < len(class_str) and class_str[i+1] == '-':
                start, end_char = class_str[i], class_str[i+2]
                for c in range(ord(start), ord(end_char)+1):
                    allowed.add(chr(c))
                i += 3
            else:
                allowed.add(class_str[i])
                i += 1
        
        def matches(char):
            if negated:
                return char not in allowed
            else:
                return char in allowed
        return matches
    
    try:
        elements = []
        i = 0
        n = len(pattern)
        
        while i < n:
            if pattern[i] == '[':
                j = i + 1
                while j < n and pattern[j] != ']':
                    j += 1
                if j >= n:
                    raise ValueError("Unclosed [...]")
                class_str = pattern[i+1:j]
                base_element = ('class', parse_char_class(class_str))
                i = j + 1
            elif pattern[i] == '.':
                base_element = ('dot', None)
                i += 1
            else:
                c = pattern[i]
                if c in '*+?':
                    raise ValueError("Invalid pattern: quantifier without preceding element")
                base_element = ('literal', c)
                i += 1
            
            # Check for quantifier after base element
            if i < n and pattern[i] in '*+?':
                quantifier = pattern[i]
                i += 1
            else:
                quantifier = None
            elements.append((base_element, quantifier))
        
        def match_helper(pattern_idx, text_idx):
            # If both are at end, success
            if pattern_idx == len(elements) and text_idx == len(text):
                return True
            # If pattern is done but text isn't, failure
            if pattern_idx == len(elements):
                return False
            
            base_element, quantifier = elements[pattern_idx]
            
            def match_base(char):
                if base_element[0] == 'literal':
                    return char == base_element[1]
                elif base_element[0] == 'dot':
                    return True
                else:  # class
                    return base_element[1](char)
            
            # Handle quantifiers
            if quantifier:
                if quantifier == '*':
                    # Try zero occurrences
                    if match_helper(pattern_idx + 1, text_idx):
                        return True
                    # Try one or more occurrences
                    j = text_idx
                    while j < len(text) and match_base(text[j]):
                        if match_helper(pattern_idx + 1, j + 1):
                            return True
                        j += 1
                elif quantifier == '+':
                    # Must have at least one occurrence
                    j = text_idx
                    if j >= len(text) or not match_base(text[j]):
                        return False
                    while j < len(text) and match_base(text[j]):
                        if match_helper(pattern_idx + 1, j + 1):
                            return True
                        j += 1
                elif quantifier == '?':
                    # Try zero occurrences
                    if match_helper(pattern_idx + 1, text_idx):
                        return True
                    # Try one occurrence
                    if text_idx < len(text) and match_base(text[text_idx]):
                        return match_helper(pattern_idx + 1, text_idx + 1)
            else:
                # No quantifier: must match exactly once
                if text_idx >= len(text) or not match_base(text[text_idx]):
                    return False
                return match_helper(pattern_idx + 1, text_idx + 1)
            
            return False
        
        return match_helper(0, 0)
    except ValueError as e:
        raise e
