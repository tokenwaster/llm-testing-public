class Element:
    def __init__(self, type, value=None, quantifier=None):
        self.type = type  # 'literal', 'wildcard', 'class'
        self.value = value  # char or (is_negated, set)
        self.quantifier = quantifier

    def matches(self, char):
        if self.type == 'literal':
            return char == self.value
        if self.type == 'wildcard':
            return True
        if self.type == 'class':
            negated, s = self.value
            return (char in s) if not negated else (char not in s)

def match(pattern: str, text: str) -> bool:
    # Parse the pattern into a list of Element objects
    elements = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char == '[':
            i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
            
            chars = set()
            while i < len(pattern) and pattern[i] != ']':
                # Check for range start-end (e.g., a-z)
                if i + 2 < len(pattern) and pattern[i+1] == '-' and pattern[i+2] != ']':
                    start = pattern[i]
                    end = pattern[i+2]
                    for c in range(ord(start), ord(end) + 1):
                        chars.add(chr(c))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed [")
            i += 1  # skip ']'
            elem = Element('class', (negated, chars))
        elif char == '.':
            elem = Element('wildcard')
            i += 1
        elif char in '*+?':
            raise ValueError("Quantifier without preceding element")
        else:
            elem = Element('literal', char)
            i += 1
        
        # Check for quantifier following the element
        if i < len(pattern) and pattern[i] in '*+?':
            elem.quantifier = pattern[i]
            i += 1
        elements.append(elem)

    def solve(elems, t_idx):
        # Base case: if no more elements to match, text must be fully consumed
        if not elems:
            return t_idx == len(text)
        
        elem = elems[0]
        rest = elems[1:]
        q = elem.quantifier
        
        if q == '*':
            # Try matching 0 times (skip the element)
            if solve(rest, t_idx):
                return True
            # Try matching 1 or more times
            if t_idx < len(text) and elem.matches(text[t_idx]):
                return solve(elems, t_idx + 1)
            return False
        
        elif q == '+':
            # Must match at least once
            if t_idx < len(text) and elem.matches(text[t_idx]):
                # After matching one, it behaves like a '*' quantifier
                temp_elem = Element(elem.type, elem.value, '*')
                return solve([temp_elem] + rest, t_idx + 1)
            return False
        
        elif q == '?':
            # Try matching 0 times (skip the element)
            if solve(rest, t_idx):
                return True
            # Try matching exactly once
            if t_idx < len(text) and elem.matches(text[t_idx]):
                return solve(rest, t_idx + 1)
            return False
        
        else:  # No quantifier (exactly one match required)
            if t_idx < len(text) and elem.matches(text[t_idx]):
                return solve(rest, t_idx + 1)
            return False

    return solve(elements, 0)
