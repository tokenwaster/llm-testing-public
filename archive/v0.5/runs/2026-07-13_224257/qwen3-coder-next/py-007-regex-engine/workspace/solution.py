def match(pattern: str, text: str) -> bool:
    """
    Match pattern against entire text using recursive backtracking.
    
    Supports:
    - literal characters
    - '.' (any single character)
    - '*' (zero or more of preceding element)
    - '+' (one or more of preceding element)
    - '?' (zero or one of preceding element)
    - character classes [abc], ranges [a-z0-9], negation [^abc]
    """
    
    def parse_char_class(pattern_str, pos):
        """Parse a character class starting at pos (after the '[')."""
        if pos >= len(pattern_str) or pattern_str[pos] != '[':
            raise ValueError("Expected '[' for character class")
        
        pos += 1
        negated = False
        if pos < len(pattern_str) and pattern_str[pos] == '^':
            negated = True
            pos += 1
        
        if pos >= len(pattern_str):
            raise ValueError("Unclosed character class")
            
        chars = set()
        while pos < len(pattern_str) and pattern_str[pos] != ']':
            if pos + 2 < len(pattern_str) and pattern_str[pos+1] == '-' and pattern_str[pos+2] != ']':
                # Range like a-z
                start_char = pattern_str[pos]
                end_char = pattern_str[pos+2]
                if ord(start_char) > ord(end_char):
                    raise ValueError(f"Invalid character range: {start_char}-{end_char}")
                for c in range(ord(start_char), ord(end_char) + 1):
                    chars.add(chr(c))
                pos += 3
            else:
                # Single character
                chars.add(pattern_str[pos])
                pos += 1
        
        if pos >= len(pattern_str):
            raise ValueError("Unclosed character class")
            
        return chars, negated, pos + 1
    
    def parse_element(pattern_str, pos):
        """Parse a regex element starting at pos. Returns (element_type, value, new_pos)."""
        if pos >= len(pattern_str):
            raise ValueError("Unexpected end of pattern")
        
        c = pattern_str[pos]
        
        # Character class
        if c == '[':
            chars, negated, new_pos = parse_char_class(pattern_str, pos)
            return ('class', (chars, negated), new_pos)
        
        # Special characters that can be standalone or followed by quantifiers
        if c in '.^$*+?':
            raise ValueError(f"Invalid pattern: '{c}' at position {pos}")
        
        # Regular character or other special chars like '\'
        return ('char', c, pos + 1)
    
    def parse_pattern(pattern_str):
        """Parse the entire pattern into a list of elements."""
        if not pattern_str:
            return []
            
        elements = []
        i = 0
        
        while i < len(pattern_str):
            # Check for quantifier at start
            if pattern_str[i] in '*+?':
                raise ValueError(f"Quantifier '{pattern_str[i]}' must follow an element")
                
            # Parse the base element
            elem_type, elem_val, new_i = parse_element(pattern_str, i)
            
            # Check for quantifier after element
            quantifier = None
            if new_i < len(pattern_str) and pattern_str[new_i] in '*+?':
                quantifier = pattern_str[new_i]
                new_i += 1
                
            elements.append((elem_type, elem_val, quantifier))
            i = new_i
            
        return elements
    
    def match_element(element, text, t_idx):
        """Check if element matches at position t_idx in text."""
        elem_type, elem_val, _ = element
        
        if t_idx >= len(text):
            return False
            
        char = text[t_idx]
        
        if elem_type == 'char':
            return elem_val == char or (elem_val == '.' and True)  # '.' matches any character
        elif elem_type == 'class':
            chars, negated = elem_val
            in_class = char in chars
            return not in_class if negated else in_class
            
        return False
    
    def match_recursive(pattern_elements, p_idx, text, t_idx):
        """Recursive backtracking matcher."""
        # Base case: pattern exhausted
        if p_idx >= len(pattern_elements):
            return t_idx >= len(text)
            
        elem_type, elem_val, quantifier = pattern_elements[p_idx]
        
        # Handle quantifiers
        if quantifier == '*':
            # Try zero occurrences first (greedy approach with backtracking)
            if match_recursive(pattern_elements, p_idx + 1, text, t_idx):
                return True
                
            # Try one or more occurrences
            while t_idx < len(text) and match_element((elem_type, elem_val, None), text, t_idx):
                t_idx += 1
                if match_recursive(pattern_elements, p_idx + 1, text, t_idx):
                    return True
                    
            return False
            
        elif quantifier == '+':
            # Must have at least one occurrence
            if not match_element((elem_type, elem_val, None), text, t_idx):
                return False
                
            t_idx += 1
            
            # Try zero more occurrences (greedy)
            if match_recursive(pattern_elements, p_idx + 1, text, t_idx):
                return True
                
            # Try one or more additional occurrences
            while t_idx < len(text) and match_element((elem_type, elem_val, None), text, t_idx):
                t_idx += 1
                if match_recursive(pattern_elements, p_idx + 1, text, t_idx):
                    return True
                    
            return False
            
        elif quantifier == '?':
            # Try zero occurrences first
            if match_recursive(pattern_elements, p_idx + 1, text, t_idx):
                return True
                
            # Try one occurrence
            if t_idx < len(text) and match_element((elem_type, elem_val, None), text, t_idx):
                return match_recursive(pattern_elements, p_idx + 1, text, t_idx + 1)
                
            return False
            
        else:  # No quantifier - must match exactly one character
            if t_idx < len(text) and match_element((elem_type, elem_val, None), text, t_idx):
                return match_recursive(pattern_elements, p_idx + 1, text, t_idx + 1)
                
            return False
    
    try:
        # Parse the pattern first to validate it
        elements = parse_pattern(pattern)
        
        # Handle empty pattern case
        if not elements:
            return len(text) == 0
            
        return match_recursive(elements, 0, text, 0)
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid pattern: {e}")
