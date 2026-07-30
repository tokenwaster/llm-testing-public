def match(pattern: str, text: str) -> bool:
    """
    Matches the ENTIRE 'text' against the given 'pattern' using a custom 
    regex-like subset including . , * , + , ? and character classes [].
    """

    # --- Parser to convert pattern string into a list of matchable elements ---
    def parse_pattern(pattern: str) -> list:
        elements = []
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            if char in '*+?':
                raise ValueError("Quantifier without preceding element")
            
            elem = None
            if char == '.':
                elem = {'type': 'dot'}
                i += 1
            elif char == '[':
                i += 1
                negate = False
                if i < len(pattern) and pattern[i] == '^':
                    negate = True
                    i += 1
                
                chars = set()
                while i < len(pattern) and pattern[i] != ']':
                    # Check for range like [a-z]
                    if (i + 2 < len(pattern) and 
                        pattern[i+1] == '-' and 
                        pattern[i+2] != ']'):
                        start_char = pattern[i]
                        end_char = pattern[i+2]
                        for code in range(ord(start_char), ord(end_char) + 1):
                            chars.add(chr(code))
                        i += 3
                    else:
                        chars.add(pattern[i])
                        i += 1
                
                if i >= len(pattern):
                    raise ValueError("Unclosed bracket")
                i += 1  # Skip closing ']'
                elem = {'type': 'class', 'chars': chars, 'negate': negate}
            else:
                elem = {'type': 'literal', 'value': char}
                i += 1
            
            if elem is None:
                raise ValueError("Invalid pattern structure")

            # Check if this element is followed by a quantifier
            if i < len(pattern) and pattern[i] in '*+?':
                elem['quantifier'] = pattern[i]
                i += 1
            else:
                elem['quantifier'] = None
            
            elements.append(elem)
        return elements

    # --- Element matching logic ---
    def matches_element(elem, char):
        if elem['type'] == 'dot':
            return True
        elif elem['type'] == 'literal':
            return char == elem['value']
        elif elem['type'] == 'class':
            chars = elem['chars']
            negate = elem['negate']
            if negate:
                # [^abc] means any character not in {a, b, c}
                # If the class is empty like [^], it matches every char.
                return char not in chars
            else:
                return char in chars
        return False

    elements = parse_pattern(pattern)
    memo = {}

    def solve(idx: int, t_idx: int) -> bool:
        # Base Case: All elements processed
        if idx == len(elements):
            return t_idx == len(text)
        
        state = (idx, t_idx)
        if state in memo:
            return memo[state]

        elem = elements[idx]
        q = elem['quantifier']
        res = False

        if q is None:
            # Exact match for one character
            if t_idx < len(text) and matches_element(elem, text[t_idx]):
                res = solve(idx + 1, t_idx + 1)
        elif q == '?':
            # Choice 1: Match zero occurrences of this element
            if solve(idx + 1, t_idx):
                res = True
            # Choice 2: Match exactly one occurrence
            elif t_idx < len(text) and matches_element(elem, text[t_idx]):
                res = solve(idx + 1, t_idx + 1)
        elif q == '*':
            # Choice 1: Match zero occurrences (skip this element)
            if solve(idx + 1, t_idx):
                res = True
            else:
                # Choice 2: Try matching one or more (greedy-style backtracking)
                curr = t_idx
                while curr < len(text) and matches_element(elem, text[curr]):
                    curr += 1
                    if solve(idx + 1, curr):
                        res = True
                        break
        elif q == '+':
            # Must match at least one character first
            curr = t_idx
            while curr < len(text) and matches_element(elem, text[curr]):
                curr += 1
                if curr > t_idx: # Ensure we matched at least one
                    if solve(idx + 1, curr):
                        res = True
                        break
        
        memo[state] = res
        return res

    return solve(0, 0)
