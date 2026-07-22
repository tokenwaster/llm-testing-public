def match(pattern: str, text: str) -> bool:
    elements = []
    i = 0
    n = len(pattern)
    while i < n:
        if pattern[i] in '*+?':
            if not elements:
                raise ValueError("Quantifier without preceding element")
            if elements[-1].get('quant'):
                raise ValueError("Multiple quantifiers")
            elements[-1]['quant'] = pattern[i]
            i += 1
            continue
        
        if pattern[i] == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            chars = set()
            while j < n and pattern[j] != ']':
                if j + 2 < n and pattern[j+1] == '-' and pattern[j+2] != ']':
                    start = pattern[j]
                    end = pattern[j+2]
                    for c in range(ord(start), ord(end)+1):
                        chars.add(chr(c))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= n or pattern[j] != ']':
                raise ValueError("Unclosed character class")
            elements.append({'type': 'class', 'chars': chars, 'negated': negated})
            i = j + 1
        elif pattern[i] == '.':
            elements.append({'type': 'dot'})
            i += 1
        else:
            elements.append({'type': 'char', 'char': pattern[i]})
            i += 1
        
        if i < n and pattern[i] in '*+?':
            if elements[-1].get('quant'):
                raise ValueError("Multiple quantifiers")
            elements[-1]['quant'] = pattern[i]
            i += 1
        else:
            elements[-1]['quant'] = None
            
    n_elem = len(elements)
    n_text = len(text)
    memo = {}

    def element_matches(elem, char):
        if elem['type'] == 'dot':
            return True
        elif elem['type'] == 'char':
            return char == elem['char']
        elif elem['type'] == 'class':
            if char in elem['chars']:
                return not elem['negated']
            else:
                return elem['negated']
        return False

    def dp(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        
        if i == n_elem:
            res = (j == n_text)
            memo[(i, j)] = res
            return res
        
        elem = elements[i]
        quant = elem.get('quant')
        
        if quant is None:
            if j < n_text and element_matches(elem, text[j]):
                res = dp(i + 1, j + 1)
            else:
                res = False
        elif quant == '?':
            if dp(i + 1, j):
                res = True
            elif j < n_text and element_matches(elem, text[j]):
                res = dp(i + 1, j + 1)
            else:
                res = False
        elif quant == '*':
            if dp(i + 1, j):
                res = True
            else:
                res = False
                while j < n_text and element_matches(elem, text[j]):
                    if dp(i + 1, j + 1):
                        res = True
                        break
                    j += 1
        elif quant == '+':
            res = False
            while j < n_text and element_matches(elem, text[j]):
                if dp(i + 1, j + 1):
                    res = True
                    break
                j += 1
        else:
            res = False
            
        memo[(i, j)] = res
        return res

    return dp(0, 0)
