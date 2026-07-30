def match(pattern: str, text: str) -> bool:
    """
    Reports whether pattern matches the entire text using a recursive backtracking matcher.
    Supports: literal, '.', '*', '+', '?', and character classes [abc], [a-z], [^abc].
    """
    
    def parse_pattern(pattern: str):
        tokens = []
        i = 0
        n = len(pattern)
        while i < n:
            # 1. Identify the Atom
            if pattern[i] == '[':
                i += 1
                negated = False
                if i < n and pattern[i] == '^':
                    negated = True
                    i += 1
                
                start_idx = i
                bracket_level = 1
                while i < n and bracket_level > 0:
                    if pattern[i] == '[':
                        bracket_level += 1
                    elif pattern[i] == ']':
                        bracket_level -= 1
                    i += 1
                
                if bracket_level > 0:
                    raise ValueError("Unclosed bracket")
                
                # i is now at the position after ']'
                content = pattern[start_idx:i-1]
                atom_set = set()
                j = 0
                while j < len(content):
                    if j + 2 < len(content) and content[j+1] == '-':
                        start_char = content[j]
                        end_char = content[j+2]
                        if ord(start_char) > ord(end_char):
                            raise ValueError("Invalid range")
                        for char_code in range(ord(start_char), ord(end_char) + 1):
                            atom_set.add(chr(char_code))
                        j += 3
                    else:
                        atom_set.add(content[j])
                        j += 1
                atom = ('class', atom_set, negated)
                # The loop index i is already past ']'
            elif pattern[i] == '.':
                atom = ('wildcard',)
                i += 1
            elif pattern[i] in '*+?':
                raise ValueError("Quantifier without preceding element")
            else:
                atom = ('literal', pattern[i])
                i += 1
            
            # 2. Identify the Quantifier
            quantifier = None
            if i < n and pattern[i] in '*+?':
                quantifier = pattern[i]
                i += 1
            
            tokens.append((atom, quantifier))
        return tokens

    tokens = parse_pattern(pattern)

    def atom_matches(char, atom):
        if atom[0] == 'literal':
            return char == atom[1]
        if atom[0] == 'wildcard':
            return True
        if atom[0] == 'class':
            is_in = char in atom[1]
            return not is_in if atom[2] else is_in
        return False

    def solve_star_logic(t_idx, token_idx, atom):
        # Helper to handle '0 or more' part (used for * and +)
        # Option 1: Match 0 more
        if solve(t_idx, token_idx + 1):
            return True
        # Option 2: Match 1 more
        if t_idx < len(text) and atom_matches(text[t_idx], atom):
            return solve_star_logic(t_idx + 1, token_idx, atom)
        return False

    def solve(t_idx, token_idx):
        # Base Case: No more tokens to match
        if token_idx == len(tokens):
            return t_idx == len(text)
        
        atom, quantifier = tokens[token_idx]
        
        # Case: No Quantifier (Exactly one)
        if quantifier is None:
            if t_idx < len(text) and atom_matches(text[t_idx], atom):
                return solve(t_idx + 1, token_idx + 1)
            return False
        
        # Case: '?' (Zero or one)
        elif quantifier == '?':
            # Try matching one
            if t_idx < len(text) and atom_matches(text[t_idx], atom):
                if solve(t_idx + 1, token_idx + 1):
                    return True
            # Try matching zero
            return solve(t_idx, token_idx + 1)
            
        # Case: '*' (Zero or more)
        elif quantifier == '*':
            # Try matching zero
            if solve(t_idx, token_idx + 1):
                return True
            # Try matching one or more
            if t_idx < len(text) and atom_matches(text[t_idx], atom):
                return solve_star_logic(t_idx + 1, token_idx, atom)
            return False
            
        # Case: '+' (One or more)
        elif quantifier == '+':
            # Must match at least one
            if t_idx < len(text) and atom_matches(text[t_idx], atom):
                # After matching one, the rest is essentially '*' logic
                return solve_star_logic(t_idx + 1, token_idx, atom)
            return False
        
        return False

    return solve(0, 0)
