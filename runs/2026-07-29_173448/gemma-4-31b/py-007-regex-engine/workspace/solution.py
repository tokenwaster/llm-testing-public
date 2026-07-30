import functools

def match(pattern: str, text: str) -> bool:
    """
    Reports whether the given pattern matches the ENTIRE text.
    Supports literal characters, '.', '*', '+', '?', and character classes [abc], [a-z0-9], [^abc].
    """

    # Parse the pattern into a list of tokens (element, quantifier)
    # Elements are represented as tuples: ('literal', char), ('dot',), or ('class', set, negated)
    tokens = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        
        # Determine the matching element
        if char == '[':
            i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            
            negated = False
            if i < len(pattern) and pattern[i] == '^':
                negated = True
                i += 1
            
            chars_set = set()
            while i < len(pattern) and pattern[i] != ']':
                # Check for range [a-z]
                if (i + 2 < len(pattern) and 
                    pattern[i+1] == '-' and 
                    pattern[i+2] != ']'):
                    start, end = pattern[i], pattern[i+2]
                    for c_code in range(ord(start), ord(end) + 1):
                        chars_set.add(chr(c_code))
                    i += 3
                else:
                    chars_set.add(pattern[i])
                    i += 1
            
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            i += 1  # Skip closing ']'
            element = ('class', chars_set, negated)
        elif char == '.':
            element = ('dot',)
            i += 1
        elif char in '*+?':
            raise ValueError("Quantifier without preceding element")
        else:
            element = ('literal', char)
            i += 1
        
        # Check for quantifier following the element
        if i < len(pattern) and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if quant == '*':
                tokens.append((element, '*'))
            elif quant == '?':
                tokens.append((element, '?'))
            elif quant == '+':
                # a+ is logically equivalent to 'a' followed by 'a*'
                tokens.append((element, None))
                tokens.append((element, '*'))
        else:
            tokens.append((element, None))

    def matches_char(element, char):
        """Check if a single character fits the element definition."""
        if element[0] == 'dot':
            return True
        if element[0] == 'literal':
            return char == element[1]
        if element[0] == 'class':
            chars_set, negated = element[1], element[2]
            is_in = char in chars_set
            return not is_in if negated else is_in
        return False

    @functools.lru_cache(None)
    def solve(t_idx: int, s_idx: int) -> bool:
        """Recursive backtracking function to check for matches."""
        # Base case: reached end of pattern tokens
        if t_idx == len(tokens):
            return s_idx == len(text)
        
        element, quant = tokens[t_idx]
        
        # Case 1: Quantifier is '*' (Zero or more matches)
        if quant == '*':
            # Option A: Match zero characters of this element and move to the next token
            if solve(t_idx + 1, s_idx):
                return True
            # Option B: Match one character and stay on the same token (for more matches)
            if s_idx < len(text) and matches_char(element, text[s_idx]):
                if solve(t_idx, s_idx + 1):
                    return True
        
        # Case 2: Quantifier is '?' (Zero or one match)
        elif quant == '?':
            # Option A: Match zero characters and move to next token
            if solve(t_idx + 1, s_idx):
                return True
            # Option B: Match exactly one character and move to next token
            if s_idx < len(text) and matches_char(element, text[s_idx]):
                if solve(t_idx + 1, s_idx + 1):
                    return True

        # Case 3: Quantifier is None (Exactly one match required)
        else:
            if s_idx < len(text) and matches_char(element, text[s_idx]):
                if solve(t_idx + 1, s_idx + 1):
                    return True
        
        return False

    return solve(0, 0)
