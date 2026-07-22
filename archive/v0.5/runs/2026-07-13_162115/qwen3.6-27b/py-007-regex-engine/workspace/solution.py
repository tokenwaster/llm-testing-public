def match(pattern: str, text: str) -> bool:
    def parse_pattern(p):
        tokens = []
        i = 0
        n = len(p)
        while i < n:
            char = p[i]
            if char in '*+?':
                if not tokens:
                    raise ValueError("Quantifier at start of pattern")
                if tokens[-1][3] is not None:
                    raise ValueError("Quantifier follows quantifier")
                tokens[-1] = list(tokens[-1])
                tokens[-1][3] = char
                tokens[-1] = tuple(tokens[-1])
                i += 1
            elif char == '[':
                j = i + 1
                if j < n and p[j] == '^':
                    j += 1
                while j < n and p[j] != ']':
                    j += 1
                if j == n:
                    raise ValueError("Unclosed character class")
                
                content = p[i+1:j]
                negate = content.startswith('^')
                if negate:
                    content = content[1:]
                
                chars = set()
                k = 0
                while k < len(content):
                    if k + 2 < len(content) and content[k+1] == '-':
                        start, end = content[k], content[k+2]
                        if ord(start) > ord(end):
                            raise ValueError("Invalid range in character class")
                        for c in range(ord(start), ord(end) + 1):
                            chars.add(chr(c))
                        k += 3
                    else:
                        chars.add(content[k])
                        k += 1
                
                tokens.append(('class', chars, negate, None))
                i = j + 1
            elif char == '.':
                tokens.append(('dot', None, None, None))
                i += 1
            else:
                tokens.append(('literal', char, None, None))
                i += 1
        return tokens

    tokens = parse_pattern(pattern)
    
    def solve(t_idx, p_idx):
        if t_idx == len(tokens):
            return p_idx == len(text)
        
        atom_type, atom_data, negate, quantifier = tokens[t_idx]
        
        def matches_atom():
            if p_idx >= len(text):
                return False
            char = text[p_idx]
            if atom_type == 'literal':
                return char == atom_data
            elif atom_type == 'dot':
                return True
            elif atom_type == 'class':
                in_class = char in atom_data
                return not in_class if negate else in_class
            return False

        if quantifier is None:
            return matches_atom() and solve(t_idx + 1, p_idx + 1)
        elif quantifier == '?':
            if matches_atom() and solve(t_idx + 1, p_idx + 1):
                return True
            return solve(t_idx + 1, p_idx)
        elif quantifier == '*':
            if solve(t_idx + 1, p_idx):
                return True
            if matches_atom() and solve(t_idx, p_idx + 1):
                return True
            return False
        elif quantifier == '+':
            if matches_atom():
                if solve(t_idx, p_idx + 1):
                    return True
                if solve(t_idx + 1, p_idx + 1):
                    return True
            return False
        return False

    return solve(0, 0)
