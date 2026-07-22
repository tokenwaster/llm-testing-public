def match(pattern: str, text: str) -> bool:
    def parse_char_class(pattern, p_idx):
        """Parse a character class starting at p_idx and return (class_matcher, end_idx)"""
        if pattern[p_idx] != '[':
            raise ValueError("Expected '['")
        
        p_idx += 1
        if p_idx >= len(pattern):
            raise ValueError("Unclosed '['")
        
        negated = False
        if pattern[p_idx] == '^':
            negated = True
            p_idx += 1
        
        if p_idx >= len(pattern):
            raise ValueError("Unclosed '['")
        
        chars = set()
        while p_idx < len(pattern) and pattern[p_idx] != ']':
            if p_idx + 2 < len(pattern) and pattern[p_idx + 1] == '-' and pattern[p_idx + 2] != ']':
                start_char = pattern[p_idx]
                end_char = pattern[p_idx + 2]
                for c in range(ord(start_char), ord(end_char) + 1):
                    chars.add(chr(c))
                p_idx += 3
            else:
                chars.add(pattern[p_idx])
                p_idx += 1
        
        if p_idx >= len(pattern):
            raise ValueError("Unclosed '['")
        
        p_idx += 1
        
        def matcher(c):
            result = c in chars
            if negated:
                result = not result
            return result
        
        return matcher, p_idx
    
    def backtrack(p_idx, t_idx):
        if p_idx >= len(pattern):
            return t_idx == len(text)
        
        if pattern[p_idx] == '[':
            char_matcher, element_end = parse_char_class(pattern, p_idx)
            element_type = 'class'
        elif pattern[p_idx] == '.':
            element_type = 'dot'
            element_end = p_idx + 1
            char_matcher = None
        elif pattern[p_idx] in '*+?':
            raise ValueError(f"'{pattern[p_idx]}' with nothing before it")
        else:
            element_type = 'literal'
            element_end = p_idx + 1
            char_matcher = None
        
        quantifier = None
        next_p_idx = element_end
        if element_end < len(pattern) and pattern[element_end] in '*+?':
            quantifier = pattern[element_end]
            next_p_idx = element_end + 1
        
        def matches_element(c):
            if element_type == 'class':
                return char_matcher(c)
            elif element_type == 'dot':
                return True
            else:
                return c == pattern[p_idx]
        
        if quantifier == '*':
            i = t_idx
            while i < len(text) and matches_element(text[i]):
                i += 1
            while i >= t_idx:
                if backtrack(next_p_idx, i):
                    return True
                i -= 1
            return False
        elif quantifier == '+':
            if t_idx >= len(text) or not matches_element(text[t_idx]):
                return False
            i = t_idx + 1
            while i < len(text) and matches_element(text[i]):
                i += 1
            while i >= t_idx + 1:
                if backtrack(next_p_idx, i):
                    return True
                i -= 1
            return False
        elif quantifier == '?':
            if t_idx < len(text) and matches_element(text[t_idx]):
                if backtrack(next_p_idx, t_idx + 1):
                    return True
            return backtrack(next_p_idx, t_idx)
        else:
            if t_idx < len(text) and matches_element(text[t_idx]):
                return backtrack(element_end, t_idx + 1)
            return False
    
    return backtrack(0, 0)
