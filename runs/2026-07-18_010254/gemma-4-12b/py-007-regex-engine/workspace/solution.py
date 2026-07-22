def match(pattern: str, text: str) -> bool:
    """
    Matches the entire text against a given regex-like pattern.
    Supports literals, '.', '*', '+', '?', and character classes [abc], [a-z0-9], [^abc].
    """

    def parse_pattern(pattern: str):
        tokens = []
        i = 0
        while i < len(pattern):
            c = pattern[i]
            if c in '*+?':
                raise ValueError("Quantifier without preceding element")
            
            matcher = None
            if c == '.':
                matcher = lambda char: True
                i += 1
            elif c == '[':
                i += 1
                negated = False
                if i < len(pattern) and pattern[i] == '^':
                    negated = True
                    i += 1
                
                j = i
                while j < len(pattern) and pattern[j] != ']':
                    j += 1
                if j >= len(pattern):
                    raise ValueError("Unclosed bracket")
                
                chars_in_class = set()
                ranges = []
                k = i
                while k < j:
                    # A range is defined by a hyphen not at the start or end of the class content.
                    if pattern[k] == '-' and k > i and k < j - 1:
                        ranges.append((pattern[k-1], pattern[k+1]))
                        k += 2  # Skip the hyphen and the character after it (already part of range)
                    else:
                        chars_in_class.add(pattern[k])
                        k += 1
                i = j + 1
                
                def make_matcher(chars, ranges, neg):
                    def matcher_func(char):
                        found = (char in chars) or any(start <= char <= end for start, end in ranges)
                        return not found if neg else found
                    return matcher_func
                
                matcher = make_matcher(chars_in_class, ranges, negated)
            else:
                # Literal character
                def make_literal_matcher(lit):
                    return lambda char: char == lit
                matcher = make_literal_matcher(c)
                i += 1
            
            if i < len(pattern) and pattern[i] in '*+?':
                quant = pattern[i]
                tokens.append((matcher, quant))
                i += 1
            else:
                tokens.append((matcher, None))
        return tokens

    tokens = parse_pattern(pattern)

    def backtrack(t_idx, s_idx):
        # Base case: if we've processed all tokens, check if we've consumed the entire text.
        if t_idx == len(tokens):
            return s_idx == len(text)
        
        matcher, quant = tokens[t_idx]
        
        if quant is None:
            # Exactly one match required.
            if s_idx < len(text) and matcher(text[s_idx]):
                return backtrack(t_idx + 1, s_idx + 1)
            return False
        
        elif quant == '*':
            # Zero or more matches.
            # Option 1: Match zero of this token and move to the next.
            if backtrack(t_idx + 1, s_idx):
                return True
            # Option 2: Match one or more of this token.
            curr = s_idx
            while curr < len(text) and matcher(text[curr]):
                if backtrack(t_idx + 1, curr + 1):
                    return True
                curr += 1
            return False
        
        elif quant == '+':
            # One or more matches.
            curr = s_idx
            while curr < len(text) and matcher(text[curr]):
                if backtrack(t_idx + 1, curr + 1):
                    return True
                curr += 1
            return False
        
        elif quant == '?':
            # Zero or one match.
            # Option 1: Match zero.
            if backtrack(t_idx + 1, s_idx):
                return True
            # Option 2: Match exactly one.
            if s_idx < len(text) and matcher(text[s_idx]):
                if backtrack(t_idx + 1, s_idx + 1):
                    return True
            return False
        
        return False

    return backtrack(0, 0)
