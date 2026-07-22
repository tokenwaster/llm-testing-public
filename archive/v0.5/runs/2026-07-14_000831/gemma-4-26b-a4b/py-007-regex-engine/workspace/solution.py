def match(pattern: str, text: str) -> bool:
    """
    Matches the entire text against a regex pattern supporting literals, '.',
    '*', '+', '?', and character classes [abc], [a-z0-9], [^abc].
    """

    def parse_class(content, negate):
        chars = set()
        idx = 0
        while idx < len(content):
            # Check for a range like 'a-z'
            if idx + 2 < len(content) and content[idx+1] == '-':
                start_c = content[idx]
                end_c = content[idx+2]
                for c in range(ord(start_c), ord(end_c) + 1):
                    chars.add(chr(c))
                idx += 3
            else:
                chars.add(content[idx])
                idx += 1
        if negate:
            return lambda c: c not in chars
        else:
            return lambda c: c in chars

    def parse_pattern(pattern):
        tokens = []
        i = 0
        while i < len(pattern):
            # 1. Determine the Atom (the element to be quantified)
            if pattern[i] == '[':
                start_idx = i
                i += 1
                if i >= len(pattern):
                    raise ValueError("Unclosed character class '['")
                
                negate = False
                if pattern[i] == '^':
                    negate = True
                    i += 1
                
                # Find the closing ']'
                j = i
                while j < len(pattern) and pattern[j] != ']':
                    j += 1
                if j >= len(pattern):
                    raise ValueError("Unclosed character class '['")
                
                content = pattern[i:j]
                atom_fn = parse_class(content, negate)
                i = j + 1
            elif pattern[i] == '.':
                atom_fn = lambda c: True
                i += 1
            else:
                char = pattern[i]
                # Use default argument to capture the current value of char in loop scope
                atom_fn = lambda c, char=char: c == char
                i += 1
            
            # 2. Determine the Quantifier
            quantifier = 'single'
            if i < len(pattern) and pattern[i] in '*+?':
                quantifier = pattern[i]
                i += 1
            
            # 3. Validate that a quantifier follows an atom
            if not tokens and quantifier in '*+?':
                raise ValueError("Quantifier without preceding element")
            
            tokens.append((atom_fn, quantifier))
        return tokens

    tokens = parse_pattern(pattern)

    def backtrack(token_idx, text_idx):
        # If all tokens are processed, check if we've consumed the entire text
        if token_idx == len(tokens):
            return text_idx == len(text)

        atom_fn, quantifier = tokens[token_idx]

        if quantifier == 'single':
            if text_idx < len(text) and atom_fn(text[text_idx]):
                return backtrack(token_idx + 1, text_idx + 1)
            return False

        elif quantifier == '?':
            # Try zero matches (skip this token)
            if backtrack(token_idx + 1, text_idx):
                return True
            # Try one match
            if text_idx < len(text) and atom_fn(text[text_idx]):
                return backtrack(token_idx + 1, text_idx + 1)
            return False

        elif quantifier == '*':
            # Try zero matches (skip this token)
            if backtrack(token_idx + 1, text_idx):
                return True
            # Try one or more matches
            curr = text_idx
            while curr < len(text) and atom_fn(text[curr]):
                curr += 1
                if backtrack(token_idx + 1, curr):
                    return True
            return False

        elif quantifier == '+':
            # Must match at least one character
            if text_idx < len(text) and atom_fn(text[text_idx]):
                # After matching the first char, it behaves like a '*' quantifier
                curr = text_idx + 1
                if backtrack(token_idx + 1, curr):
                    return True
                while curr < len(text) and atom_fn(text[curr]):
                    curr += 1
                    if backtrack(token_idx + 1, curr):
                        return True
            return False
        
        return False

    return backtrack(0, 0)
