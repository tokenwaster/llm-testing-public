def match(pattern: str, text: str) -> bool:
    """
    Reports whether the given pattern matches the entire text.
    Supports literal characters, '.', '*', '+', '?', and character classes [abc], [a-z0-9], [^abc].
    """
    elements = []
    i = 0
    while i < len(pattern):
        # Identify the atom (the element to be quantified)
        if pattern[i] == '[':
            i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
                if i >= len(pattern):
                    raise ValueError("Unclosed [")
            
            chars = set()
            while i < len(pattern) and pattern[i] != ']':
                # Handle ranges like a-z
                if i + 2 < len(pattern) and pattern[i+1] == '-' and pattern[i+2] != ']':
                    start, end = pattern[i], pattern[i+2]
                    for char_code in range(ord(start), ord(end) + 1):
                        chars.add(chr(char_code))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            
            atom = ('class', chars, negated)
            i += 1  # skip ']'
        elif pattern[i] == '.':
            atom = ('dot', None, None)
            i += 1
        elif pattern[i] in '*+?':
            raise ValueError("Quantifier without preceding element")
        else:
            atom = ('literal', pattern[i], None)
            i += 1

        # Identify the quantifier for the atom
        if i < len(pattern) and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if quant == '+':
                # a+ is equivalent to 'a' followed by 'a*'
                elements.append((atom, '1'))
                elements.append((atom, '*'))
            elif quant == '*':
                elements.append((atom, '*'))
            elif quant == '?':
                elements.append((atom, '?'))
        else:
            elements.append((atom, '1'))

    def char_matches(atom, c):
        """Helper to check if a character matches an atom."""
        if atom[0] == 'dot':
            return True
        if atom[0] == 'literal':
            return c == atom[1]
        if atom[0] == 'class':
            is_in = c in atom[1]
            return not is_in if atom[2] else is_in
        return False

    def solve(e_idx, t_idx):
        """Recursive backtracking matcher."""
        # Base case: reached the end of the pattern elements
        if e_idx == len(elements):
            return t_idx == len(text)

        atom, quant = elements[e_idx]

        if quant == '1':
            # Must match exactly one character
            if t_idx < len(text) and char_matches(atom, text[t_idx]):
                return solve(e_idx + 1, t_idx + 1)
            return False
        
        elif quant == '?':
            # Option 1: Match zero characters (skip this element)
            if solve(e_idx + 1, t_idx):
                return True
            # Option 2: Match exactly one character
            if t_idx < len(text) and char_matches(atom, text[t_idx]):
                if solve(e_idx + 1, t_idx + 1):
                    return True
            return False
        
        elif quant == '*':
            # Option 1: Match zero characters (skip this element)
            if solve(e_idx + 1, t_idx):
                return True
            # Option 2: Match one character and stay on the same element to potentially match more
            if t_idx < len(text) and char_matches(atom, text[t_idx]):
                if solve(e_idx, t_idx + 1):
                    return True
            return False
        
        return False

    return solve(0, 0)
