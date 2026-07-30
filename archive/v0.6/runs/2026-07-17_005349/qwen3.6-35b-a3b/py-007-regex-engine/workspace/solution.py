def match(pattern: str, text: str) -> bool:
    def parse(pattern):
        tokens = []
        i = 0
        n = len(pattern)
        while i < n:
            c = pattern[i]
            if c in '*+?':
                raise ValueError("Quantifier without preceding element")
            
            if c == '[':
                j = i + 1
                negated = False
                if j < n and pattern[j] == '^':
                    negated = True
                    j += 1
                chars = set()
                if j < n and pattern[j] == ']':
                    chars.add(']')
                    j += 1
                while j < n and pattern[j] != ']':
                    if j + 2 < n and pattern[j+1] == '-' and pattern[j+2] != ']':
                        start_c = pattern[j]
                        end_c = pattern[j+2]
                        if ord(start_c) > ord(end_c):
                            raise ValueError("Invalid range")
                        for k in range(ord(start_c), ord(end_c) + 1):
                            chars.add(chr(k))
                        j += 3
                    else:
                        chars.add(pattern[j])
                        j += 1
                if j >= n:
                    raise ValueError("Unclosed character class")
                if not chars:
                    raise ValueError("Empty character class")
                tokens.append({'type': 'CLASS', 'chars': chars, 'negated': negated})
                i = j + 1
            elif c == '.':
                tokens.append({'type': 'DOT'})
                i += 1
            else:
                tokens.append({'type': 'LIT', 'char': c})
                i += 1
                
            if i < n and pattern[i] in '*+?':
                tokens[-1]['quantifier'] = pattern[i]
                i += 1
                if i < n and pattern[i] in '*+?':
                    raise ValueError("Invalid quantifier sequence")
            else:
                tokens[-1]['quantifier'] = None
            i += 1
        return tokens

    tokens = parse(pattern)
    memo = {}
    
    def dp(ti, si):
        if (ti, si) in memo:
            return memo[(ti, si)]
        
        if ti == len(tokens):
            res = (si == len(text))
            memo[(ti, si)] = res
            return res
        
        token = tokens[ti]
        t_type = token['type']
        quantifier = token.get('quantifier')
        
        def matches_char(c):
            if t_type == 'LIT':
                return c == token['char']
            elif t_type == 'DOT':
                return True
            elif t_type == 'CLASS':
                return (c in token['chars']) != token['negated']
            return False

        if quantifier is None:
            if si < len(text) and matches_char(text[si]):
                res = dp(ti + 1, si + 1)
            else:
                res = False
        elif quantifier == '?':
            if si < len(text) and matches_char(text[si]):
                if dp(ti + 1, si + 1):
                    res = True
                else:
                    res = dp(ti + 1, si)
            else:
                res = dp(ti + 1, si)
        elif quantifier == '*':
            res = False
            for k in range(len(text) - si, -1, -1):
                if k > 0 and not matches_char(text[si + k - 1]):
                    break
                if dp(ti + 1, si + k):
                    res = True
                    break
        elif quantifier == '+':
            res = False
            for k in range(len(text) - si, 0, -1):
                if not matches_char(text[si + k - 1]):
                    break
                if dp(ti + 1, si + k):
                    res = True
                    break
        
        memo[(ti, si)] = res
        return res

    return dp(0, 0)
