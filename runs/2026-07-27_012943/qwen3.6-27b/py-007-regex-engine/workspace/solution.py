import sys

# Increase recursion depth to handle cases with long texts and quantifiers
try:
    sys.setrecursionlimit(5000)
except ValueError:
    pass

def match(pattern: str, text: str) -> bool:
    """
    Matches the pattern against the entire text using recursive backtracking.
    Supports literals, ., *, +, ?, and character classes [...] with ranges and negation.
    """
    
    # --- Parsing Phase ---
    tokens = []
    i = 0
    n = len(pattern)
    
    while i < n:
        char = pattern[i]
        
        # Check for quantifiers (*, +, ?) modifying the preceding element
        if char in '*+?':
            if not tokens:
                raise ValueError("Quantifier at start of pattern")
            last_token = tokens[-1]
            # Check for double quantifiers (e.g., a**)
            if 'quant' in last_token:
                raise ValueError("Invalid double quantifier")
            last_token['quant'] = char
            i += 1
            continue
        
        if char == '[':
            # Parse character class [...]
            j = i + 1
            content = []
            found_close = False
            while j < n:
                if pattern[j] == ']':
                    found_close = True
                    break
                content.append(pattern[j])
                j += 1
            
            if not found_close:
                raise ValueError("Unclosed bracket")
            
            # Process class content
            class_str = "".join(content)
            negate = False
            if class_str.startswith('^'):
                negate = True
                class_str = class_str[1:]
            
            class_chars = set()
            k = 0
            while k < len(class_str):
                c1 = class_str[k]
                # Check for range x-y
                if k + 2 < len(class_str) and class_str[k+1] == '-':
                    c2 = class_str[k+2]
                    if ord(c1) <= ord(c2):
                        for code in range(ord(c1), ord(c2) + 1):
                            class_chars.add(chr(code))
                        k += 3
                    else:
                        raise ValueError("Invalid range in character class")
                else:
                    class_chars.add(c1)
                    k += 1
            
            # Create match function for the class
            def make_class_matcher(chars, is_neg):
                def matcher(ch):
                    if is_neg:
                        return ch not in chars
                    return ch in chars
                return matcher
            
            tokens.append({
                'match': make_class_matcher(class_chars, negate)
            })
            i = j + 1
            continue
        
        elif char == '.':
            tokens.append({
                'match': lambda x: True
            })
            i += 1
        else:
            # Literal character
            val = char
            tokens.append({
                'match': lambda x, v=val: x == v
            })
            i += 1

    # --- Matching Phase (Recursive Backtracking with Memoization) ---
    memo = {}

    def solve(idx, text_idx):
        # Base case: if we consumed all pattern tokens, check if text is also exhausted
        if idx == len(tokens):
            return text_idx == len(text)
        
        state = (idx, text_idx)
        if state in memo:
            return memo[state]
        
        token = tokens[idx]
        match_func = token['match']
        quant = token.get('quant', None)
        
        # Check if current text character matches the token's criteria
        current_char_match = False
        if text_idx < len(text):
            current_char_match = match_func(text[text_idx])
        
        result = False
        
        if quant == '*':
            # Zero or more: try skipping (0 matches) or consuming (1+ matches)
            # Option 1: Match 0 times (skip token)
            if solve(idx + 1, text_idx):
                result = True
            # Option 2: Match 1+ times (consume char and stay on token)
            elif current_char_match and solve(idx, text_idx + 1):
                result = True
        
        elif quant == '+':
            # One or more: must match current char, then try continuing or stopping
            if current_char_match:
                # Option 1: Continue the + loop (match more)
                if solve(idx, text_idx + 1):
                    result = True
                # Option 2: Stop the + loop (move to next token)
                elif solve(idx + 1, text_idx + 1):
                    result = True
        
        elif quant == '?':
            # Zero or one: try skipping (0 matches) or consuming (1 match)
            # Option 1: Match 0 times (skip token)
            if solve(idx + 1, text_idx):
                result = True
            # Option 2: Match 1 time (consume char and move to next token)
            elif current_char_match and solve(idx + 1, text_idx + 1):
                result = True
        
        else:
            # Default: exactly one match
            if current_char_match and solve(idx + 1, text_idx + 1):
                result = True
        
        memo[state] = result
        return result

    return solve(0, 0)
