def match(pattern: str, text: str) -> bool:
    def helper(p_idx, t_idx):
        if p_idx == len(pattern):
            return t_idx == len(text)
        
        current_char = pattern[p_idx]
        
        element = None
        new_p_idx = p_idx
        modifier = None
        
        if current_char == '[':
            close_bracket_pos = p_idx + 1
            while close_bracket_pos < len(pattern) and pattern[close_bracket_pos] != ']':
                close_bracket_pos += 1
            
            if close_bracket_pos >= len(pattern):
                raise ValueError("Unclosed [...] in pattern")
            
            class_str = pattern[p_idx+1:close_bracket_pos]
            negated = False
            if class_str.startswith('^'):
                negated = True
                class_str = class_str[1:]
            
            allowed_chars = set()
            i = 0
            while i < len(class_str):
                current_c = class_str[i]
                if i + 2 < len(class_str) and class_str[i+1] == '-':
                    start_char = current_c
                    end_char = class_str[i+2]
                    if ord(start_char) <= ord(end_char):
                        for code in range(ord(start_char), ord(end_char)+1):
                            allowed_chars.add(chr(code))
                    else:
                        allowed_chars.add(start_char)
                        allowed_chars.add('-')
                        allowed_chars.add(end_char)
                    i += 3
                else:
                    allowed_chars.add(current_c)
                    i += 1
            
            element = (allowed_chars, negated)
            new_p_idx = close_bracket_pos + 1
        else:
            if current_char in '*+?':
                raise ValueError("Invalid pattern: modifier without preceding element")
            element = current_char
            new_p_idx = p_idx + 1
        
        if new_p_idx < len(pattern):
            mod_char = pattern[new_p_idx]
            if mod_char in '*+?':
                modifier = mod_char
                new_p_idx += 1
        
        def is_match():
            nonlocal t_idx
            if t_idx >= len(text):
                return False
            if isinstance(element, tuple):  # character class
                allowed_chars, negated = element
                return (text[t_idx] in allowed_chars) == (not negated)
            else:  # literal or '.'
                if element == '.':
                    return True
                else:
                    return text[t_idx] == element
        
        if modifier is None:
            if not is_match():
                return False
            return helper(new_p_idx, t_idx + 1)
        elif modifier == '*':
            return helper(new_p_idx, t_idx) or (is_match() and helper(p_idx, t_idx + 1))
        elif modifier == '+':
            if not is_match():
                return False
            return helper(new_p_idx, t_idx + 1) or helper(p_idx, t_idx + 1)
        elif modifier == '?':
            return helper(new_p_idx, t_idx) or (is_match() and helper(new_p_idx, t_idx + 1))
    
    try:
        return helper(0, 0)
    except ValueError as e:
        raise e
