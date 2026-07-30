def match(pattern: str, text: str) -> bool:
    def parse_char_class(p, start_idx):
        """
        Parse character class starting at start_idx (pointing to '[').
        Returns (matcher_func, next_idx) or raises ValueError.
        """
        idx = start_idx + 1  # skip '['
        
        if idx >= len(p):
            raise ValueError("Unclosed character class")
        
        negate = False
        if p[idx] == '^':
            negate = True
            idx += 1
        
        if idx >= len(p):
            raise ValueError("Unclosed character class")
        
        chars = set()
        ranges = []
        
        while idx < len(p) and p[idx] != ']':
            if idx + 2 < len(p) and p[idx + 1] == '-' and p[idx + 2] != ']':
                start_char = p[idx]
                end_char = p[idx + 2]
                ranges.append((start_char, end_char))
                idx += 3
            else:
                chars.add(p[idx])
                idx += 1
        
        if idx >= len(p):
            raise ValueError("Unclosed character class")
        
        idx += 1  # skip ']'
        
        def make_matcher(chars, ranges, negate):
            def matches(c):
                in_class = c in chars or any(s <= c <= e for s, e in ranges)
                return (not in_class) if negate else in_class
            return matches
        
        return make_matcher(chars, ranges, negate), idx
    
    def helper(p_idx, t_idx):
        """Match pattern[p_idx:] with text[t_idx:]"""
        
        if p_idx >= len(pattern):
            return t_idx >= len(text)
        
        if pattern[p_idx] == '[':
            matcher, next_p = parse_char_class(pattern, p_idx)
        else:
            ch = pattern[p_idx]
            if ch == '.':
                matcher = lambda c: True
            else:
                matcher = lambda c, ch=ch: c == ch
            next_p = p_idx + 1
        
        has_quantifier = next_p < len(pattern) and pattern[next_p] in '*+?'
        quantifier = None
        if has_quantifier:
            quantifier = pattern[next_p]
            next_p += 1
        
        if quantifier == '*':
            if helper(next_p, t_idx):
                return True
            count = 0
            while t_idx + count < len(text) and matcher(text[t_idx + count]):
                count += 1
                if helper(next_p, t_idx + count):
                    return True
            return False
        
        elif quantifier == '+':
            if t_idx >= len(text) or not matcher(text[t_idx]):
                return False
            if helper(next_p, t_idx + 1):
                return True
            count = 1
            while t_idx + count < len(text) and matcher(text[t_idx + count]):
                count += 1
                if helper(next_p, t_idx + count):
                    return True
            return False
        
        elif quantifier == '?':
            if helper(next_p, t_idx):
                return True
            if t_idx < len(text) and matcher(text[t_idx]):
                return helper(next_p, t_idx + 1)
            return False
        
        else:
            if t_idx >= len(text) or not matcher(text[t_idx]):
                return False
            return helper(next_p, t_idx + 1)
    
    if pattern:
        if pattern[0] in '*+?':
            raise ValueError("Quantifier at start of pattern")
        
        for i in range(1, len(pattern)):
            if pattern[i] in '*+?' and pattern[i-1] in '*+?':
                raise ValueError("Consecutive quantifiers")
    
    i = 0
    while i < len(pattern):
        if pattern[i] == '[':
            _, next_i = parse_char_class(pattern, i)
            i = next_i
        else:
            i += 1
    
    return helper(0, 0)
