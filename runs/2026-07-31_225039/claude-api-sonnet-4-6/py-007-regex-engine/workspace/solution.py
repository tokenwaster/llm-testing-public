def match(pattern: str, text: str) -> bool:
    """
    Match pattern against the entire text using recursive backtracking.
    Supports: literals, '.', '*', '+', '?', character classes [abc], [a-z], [^abc]
    """
    
    def parse_class(pattern: str, pos: int):
        """
        Parse a character class starting at pos (pos points to '[').
        Returns (char_test_func, new_pos) where new_pos is after ']'.
        """
        pos += 1  # skip '['
        if pos >= len(pattern):
            raise ValueError("Unclosed character class '['")
        
        negate = False
        if pos < len(pattern) and pattern[pos] == '^':
            negate = True
            pos += 1
        
        chars = set()
        ranges = []
        
        if pos >= len(pattern):
            raise ValueError("Unclosed character class '['")
        
        # First char can be ']' to include literal ']'
        first = True
        while pos < len(pattern) and (first or pattern[pos] != ']'):
            first = False
            if pos + 2 < len(pattern) and pattern[pos + 1] == '-' and pattern[pos + 2] != ']':
                # Range
                start_char = pattern[pos]
                end_char = pattern[pos + 2]
                ranges.append((start_char, end_char))
                pos += 3
            else:
                chars.add(pattern[pos])
                pos += 1
        
        if pos >= len(pattern):
            raise ValueError("Unclosed character class '['")
        
        pos += 1  # skip ']'
        
        def test(c):
            in_class = c in chars or any(s <= c <= e for s, e in ranges)
            return not in_class if negate else in_class
        
        return test, pos
    
    def parse_tokens(pattern: str):
        """
        Parse pattern into list of (element, quantifier) tuples.
        element is either a char, '.', or a test function (for classes).
        quantifier is '', '*', '+', or '?'.
        """
        tokens = []
        pos = 0
        while pos < len(pattern):
            c = pattern[pos]
            if c == '[':
                test_func, pos = parse_class(pattern, pos)
                element = test_func
            elif c in ('*', '+', '?'):
                raise ValueError(f"Quantifier '{c}' without preceding element at position {pos}")
            elif c == '\\':
                if pos + 1 >= len(pattern):
                    raise ValueError("Trailing backslash in pattern")
                pos += 1
                element = pattern[pos]
                pos += 1
            else:
                element = c
                pos += 1
            
            # Check for quantifier
            quantifier = ''
            if pos < len(pattern) and pattern[pos] in ('*', '+', '?'):
                quantifier = pattern[pos]
                pos += 1
            
            tokens.append((element, quantifier))
        
        return tokens
    
    def element_matches(element, char: str) -> bool:
        """Check if element matches a single character."""
        if callable(element):
            return element(char)
        elif element == '.':
            return True
        else:
            return element == char
    
    def backtrack(tokens, ti: int, text: str, si: int) -> bool:
        """
        Try to match tokens[ti:] against text[si:].
        """
        # Base case: no more tokens
        if ti == len(tokens):
            return si == len(text)
        
        element, quantifier = tokens[ti]
        
        if quantifier == '':
            # Must match exactly one character
            if si >= len(text):
                return False
            if not element_matches(element, text[si]):
                return False
            return backtrack(tokens, ti + 1, text, si + 1)
        
        elif quantifier == '?':
            # Zero or one
            # Try one first, then zero
            if si < len(text) and element_matches(element, text[si]):
                if backtrack(tokens, ti + 1, text, si + 1):
                    return True
            return backtrack(tokens, ti + 1, text, si)
        
        elif quantifier == '*':
            # Zero or more - try greedy then backtrack
            # Find max match
            max_si = si
            while max_si < len(text) and element_matches(element, text[max_si]):
                max_si += 1
            # Try from max down to 0
            for count in range(max_si - si, -1, -1):
                if backtrack(tokens, ti + 1, text, si + count):
                    return True
            return False
        
        elif quantifier == '+':
            # One or more
            max_si = si
            while max_si < len(text) and element_matches(element, text[max_si]):
                max_si += 1
            # Need at least one
            for count in range(max_si - si, 0, -1):
                if backtrack(tokens, ti + 1, text, si + count):
                    return True
            return False
        
        return False
    
    # Validate: check for leading quantifiers more carefully
    # parse_tokens will raise ValueError for leading quantifiers
    tokens = parse_tokens(pattern)
    
    return backtrack(tokens, 0, text, 0)
