def match(pattern: str, text: str) -> bool:
    def validate_pattern(p):
        i = 0
        while i < len(p):
            if p[i] == '*':
                if i == 0 or p[i - 1] in '*+?' or p[i - 1] == '[':
                    raise ValueError()
            elif p[i] == '+':
                if i == 0 or p[i - 1] in '*+?' or p[i - 1] == '[':
                    raise ValueError()
            elif p[i] == '?':
                if i == 0 or p[i - 1] in '*+?' or p[i - 1] == '[':
                    raise ValueError()
            elif p[i] == '[':
                if p.find(']', i + 1) == -1:
                    raise ValueError()
                i = p.find(']', i + 1)
            i += 1
    
    def matches_in_class(char, class_content):
        if not class_content:
            return False
        
        negated = class_content[0] == '^'
        content = class_content[1:] if negated else class_content
        
        result = False
        i = 0
        while i < len(content):
            if i + 2 < len(content) and content[i + 1] == '-':
                if content[i] <= char <= content[i + 2]:
                    result = True
                    break
                i += 3
            else:
                if char == content[i]:
                    result = True
                    break
                i += 1
        
        return (not result) if negated else result
    
    def match_here(p, t):
        if p == len(pattern):
            return t == len(text)
        
        if pattern[p] == '[':
            return match_class(p, t)
        
        if p + 1 < len(pattern) and pattern[p + 1] in '*+?':
            return match_quantified(p, t)
        
        if t >= len(text):
            return False
        if pattern[p] == '.':
            return match_here(p + 1, t + 1)
        elif pattern[p] == text[t]:
            return match_here(p + 1, t + 1)
        else:
            return False
    
    def match_quantified(p, t):
        element = pattern[p]
        quantifier = pattern[p + 1]
        next_p = p + 2
        
        if quantifier == '*':
            if match_here(next_p, t):
                return True
            if t < len(text) and (element == '.' or element == text[t]):
                if match_here(p, t + 1):
                    return True
            return False
        
        elif quantifier == '+':
            if t >= len(text) or (element != '.' and element != text[t]):
                return False
            if match_here(next_p, t + 1):
                return True
            if match_here(p, t + 1):
                return True
            return False
        
        elif quantifier == '?':
            if match_here(next_p, t):
                return True
            if t < len(text) and (element == '.' or element == text[t]):
                if match_here(next_p, t + 1):
                    return True
            return False
    
    def match_class(p, t):
        close_idx = pattern.find(']', p + 1)
        class_content = pattern[p + 1:close_idx]
        next_p = close_idx + 1
        
        if next_p < len(pattern) and pattern[next_p] in '*+?':
            quantifier = pattern[next_p]
            next_p += 1
            
            if quantifier == '*':
                if match_here(next_p, t):
                    return True
                if t < len(text) and matches_in_class(text[t], class_content):
                    if match_class(p, t + 1):
                        return True
                return False
            
            elif quantifier == '+':
                if t >= len(text) or not matches_in_class(text[t], class_content):
                    return False
                if match_here(next_p, t + 1):
                    return True
                if match_class(p, t + 1):
                    return True
                return False
            
            elif quantifier == '?':
                if match_here(next_p, t):
                    return True
                if t < len(text) and matches_in_class(text[t], class_content):
                    if match_here(next_p, t + 1):
                        return True
                return False
        
        else:
            if t >= len(text) or not matches_in_class(text[t], class_content):
                return False
            return match_here(next_p, t + 1)
    
    validate_pattern(pattern)
    return match_here(0, 0)
