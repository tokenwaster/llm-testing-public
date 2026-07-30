def match(pattern: str, text: str) -> bool:
    def parse_pattern(pat):
        tokens = []
        i = 0
        n = len(pat)
        while i < n:
            ch = pat[i]
            if ch in '*+?':
                raise ValueError("Quantifier cannot appear at start or after another quantifier")
            
            if ch == '[':
                i += 1
                negated = False
                if i < n and pat[i] == '^':
                    negated = True
                    i += 1
                
                ranges = []
                # First char in class can be ']'
                if i < n and pat[i] == ']':
                    ranges.append((']', ']'))
                    i += 1
                    
                while i < n and pat[i] != ']':
                    start_ch = pat[i]
                    i += 1
                    if i < n and pat[i] == '-' and i + 1 < n and pat[i+1] != ']':
                        end_ch = pat[i+1]
                        i += 2
                        ranges.append((start_ch, end_ch))
                    else:
                        ranges.append((start_ch, start_ch))
                        
                if i >= n or pat[i] != ']':
                    raise ValueError("Unclosed character class")
                i += 1
                current_spec = ('CLASS', negated, ranges)
                
            elif ch == '.':
                current_spec = ('DOT', None)
                i += 1
            else:
                current_spec = ('LITERAL', ch)
                i += 1
                
            if i < n and pat[i] in '*+?':
                q = pat[i]
                i += 1
                tokens.append((current_spec, q))
            else:
                tokens.append((current_spec, None))
                
        return tokens

    def matches_spec(spec, char):
        t = spec[0]
        if t == 'LITERAL':
            return char == spec[1]
        elif t == 'DOT':
            return True
        elif t == 'CLASS':
            negated, ranges = spec[1], spec[2]
            matched = False
            for r in ranges:
                if r[0] <= char <= r[1]:
                    matched = True
                    break
            return not matched if negated else matched
        return False

    tokens = parse_pattern(pattern)

    def solve(t_idx, txt_idx):
        if t_idx == len(tokens):
            return txt_idx == len(text)
            
        spec, quant = tokens[t_idx]
        
        # Compute max possible matches for greedy backtracking
        max_k = 0
        while txt_idx + max_k < len(text) and matches_spec(spec, text[txt_idx + max_k]):
            max_k += 1
            
        if quant == '*':
            for k in range(max_k, -1, -1):
                if solve(t_idx + 1, txt_idx + k):
                    return True
            return False
        elif quant == '+':
            for k in range(max_k, 0, -1):
                if solve(t_idx + 1, txt_idx + k):
                    return True
            return False
        elif quant == '?':
            # Try matching 1 char first (greedy)
            if max_k >= 1 and solve(t_idx + 1, txt_idx + 1):
                return True
            return solve(t_idx + 1, txt_idx)
        else: # NONE or default
            if max_k >= 1 and solve(t_idx + 1, txt_idx + 1):
                return True
            return False

    return solve(0, 0)
