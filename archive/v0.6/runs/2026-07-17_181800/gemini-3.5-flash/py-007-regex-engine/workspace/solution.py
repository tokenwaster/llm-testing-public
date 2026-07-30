def match(pattern: str, text: str) -> bool:
    # Parse the pattern into a list of tokens.
    # A token is a dictionary:
    # {
    #   'type': 'char' or 'class',
    #   'char': str (if 'char'),
    #   'match_fn': function(char) -> bool (if 'class'),
    #   'quantifier': None, '*', '+', or '?'
    # }
    tokens = []
    i = 0
    n = len(pattern)
    
    while i < n:
        char = pattern[i]
        if char in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{char}' without preceding element")
        
        if char == '.':
            token = {'type': 'char', 'char': '.', 'quantifier': None}
            i += 1
        elif char == '[':
            # Parse character class
            start_idx = i
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
                if i >= n:
                    raise ValueError("Unclosed character class")
            
            # Read until closing ']'
            class_content = []
            closed = False
            while i < n:
                if pattern[i] == ']':
                    closed = True
                    i += 1
                    break
                class_content.append(pattern[i])
                i += 1
            
            if not closed:
                raise ValueError("Unclosed character class")
            
            # Parse ranges and individual characters from class_content
            # e.g., a-z, 0-9, or individual chars
            allowed_chars = set()
            ranges = [] # list of tuples (start, end)
            
            j = 0
            m = len(class_content)
            while j < m:
                if j + 2 < m and class_content[j+1] == '-':
                    start_c = class_content[j]
                    end_c = class_content[j+2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError("Invalid range in character class")
                    ranges.append((start_c, end_c))
                    j += 3
                else:
                    allowed_chars.add(class_content[j])
                    j += 1
            
            def make_match_fn(allowed=allowed_chars, rgs=ranges, neg=negated):
                def match_fn(c: str) -> bool:
                    # Check if c is in allowed or ranges
                    in_class = (c in allowed) or any(start <= c <= end for start, end in rgs)
                    return not in_class if neg else in_class
                return match_fn
            
            token = {'type': 'class', 'match_fn': make_match_fn(), 'quantifier': None}
        else:
            # Literal character
            token = {'type': 'char', 'char': char, 'quantifier': None}
            i += 1
            
        # Check if a quantifier follows
        if i < n and pattern[i] in ('*', '+', '?'):
            token['quantifier'] = pattern[i]
            i += 1
            
        tokens.append(token)
        
    # Helper to check if a single character matches a token
    def token_matches(tok, char: str) -> bool:
        if tok['type'] == 'char':
            return tok['char'] == '.' or tok['char'] == char
        else:
            return tok['match_fn'](char)

    # Recursive backtracking matcher
    # memoization to avoid exponential complexity on certain patterns
    memo = {}
    
    def backtrack(t_idx: int, s_idx: int) -> bool:
        state = (t_idx, s_idx)
        if state in memo:
            return memo[state]
            
        # If we reached the end of tokens, we must have consumed all text
        if t_idx == len(tokens):
            res = (s_idx == len(text))
            memo[state] = res
            return res
            
        tok = tokens[t_idx]
        quant = tok['quantifier']
        
        if quant is None:
            if s_idx < len(text) and token_matches(tok, text[s_idx]):
                res = backtrack(t_idx + 1, s_idx + 1)
            else:
                res = False
        elif quant == '?':
            # Option 1: match 0 times
            if backtrack(t_idx + 1, s_idx):
                res = True
            # Option 2: match 1 time
            elif s_idx < len(text) and token_matches(tok, text[s_idx]) and backtrack(t_idx + 1, s_idx + 1):
                res = True
            else:
                res = False
        elif quant == '*':
            # Option 1: match 0 times and move to next token
            if backtrack(t_idx + 1, s_idx):
                res = True
            else:
                # Option 2: match 1 or more times (consume one char and stay on same token)
                if s_idx < len(text) and token_matches(tok, text[s_idx]) and backtrack(t_idx, s_idx + 1):
                    res = True
                else:
                    res = False
        elif quant == '+':
            # Must match at least once
            if s_idx < len(text) and token_matches(tok, text[s_idx]):
                # After matching once, it behaves like * (can match 0 or more of the same token)
                # We can transition to a state where we treat this token as having a '*' quantifier,
                # or simply backtrack with the choice of staying on '+' or moving to next token.
                # To keep it simple, we can either:
                # - move to next token (matched exactly once)
                # - stay on '+' to match more (matched once, and we continue matching)
                if backtrack(t_idx + 1, s_idx + 1) or backtrack(t_idx, s_idx + 1):
                    res = True
                else:
                    res = False
            else:
                res = False
                
        memo[state] = res
        return res

    return backtrack(0, 0)
