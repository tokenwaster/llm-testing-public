def match(pattern: str, text: str) -> bool:
    """Match pattern against entire text using recursive backtracking."""
    
    # Parse pattern into tokens: each token is (element_type, element_data, negate_flag)
    # optionally followed by a quantifier (*, +, ?) as a 4th element.
    tokens = []
    i = 0
    
    if len(pattern) > 0 and pattern[0] in '*+?':
        raise ValueError("Quantifier without preceding element")
    
    while i < len(pattern):
        c = pattern[i]
        
        if c == '[':
            # Parse character class [...]
            j = i + 1
            negate = False
            if j < len(pattern) and pattern[j] == '^':
                negate = True
                j += 1
            
            chars = set()
            while j < len(pattern) and pattern[j] != ']':
                # Check for range syntax: x-y
                if j + 2 < len(pattern) and pattern[j+1] == '-':
                    start_char = pattern[j]
                    end_char = pattern[j+2]
                    for k in range(ord(start_char), ord(end_char) + 1):
                        chars.add(chr(k))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            
            if j >= len(pattern):
                raise ValueError("Unclosed character class '['")
            
            tokens.append(('class', frozenset(chars), negate))
            i = j + 1
        
        elif c == '.':
            tokens.append(('dot', None, False))
            i += 1
        
        else:
            # Literal character (including *, +, ?, [, ], ^, - when not in special context)
            tokens.append(('literal', c, False))
            i += 1
        
        # Check for quantifier after the element
        if i < len(pattern) and pattern[i] in '*+?':
            quant = pattern[i]
            tokens[-1] = (tokens[-1][0], tokens[-1][1], tokens[-1][2], quant)
            i += 1
    
    # Helper to check if a character matches an element
    def char_matches(c, elem_type, elem_data, negate):
        if elem_type == 'literal':
            return c == elem_data
        elif elem_type == 'dot':
            return True
        elif elem_type == 'class':
            if negate:
                return c not in elem_data
            else:
                return c in elem_data
    
    # Recursive matching function with backtracking
    def match_here(ti, si):
        """Try to match tokens[ti:] against text[si:]."""
        if ti == len(tokens):
            return si == len(text)
        
        token = tokens[ti]
        elem_type = token[0]
        elem_data = token[1]
        negate = token[2]
        quant = token[3] if len(token) > 3 else None
        
        def cm(c):
            return char_matches(c, elem_type, elem_data, negate)
        
        if quant is None:
            # No quantifier: must match exactly one character
            if si < len(text) and cm(text[si]):
                return match_here(ti + 1, si + 1)
            return False
        
        if quant == '*':
            # Zero or more of preceding element (greedy with backtracking)
            max_copies = 0
            pos = si
            while pos < len(text) and cm(text[pos]):
                max_copies += 1
                pos += 1
            for num in range(max_copies, -1, -1):
                if match_here(ti + 1, si + num):
                    return True
            return False
        
        elif quant == '+':
            # One or more of preceding element (greedy with backtracking)
            if si >= len(text) or not cm(text[si]):
                return False
            max_copies = 0
            pos = si
            while pos < len(text) and cm(text[pos]):
                max_copies += 1
                pos += 1
            for num in range(max_copies, 0, -1):
                if match_here(ti + 1, si + num):
                    return True
            return False
        
        elif quant == '?':
            # Zero or one of preceding element (non-greedy)
            # Try matching 0 occurrences first
            if match_here(ti + 1, si):
                return True
            # Try matching 1 occurrence
            if si < len(text) and cm(text[si]):
                if match_here(ti + 1, si + 1):
                    return True
            return False
    
    return match_here(0, 0)
