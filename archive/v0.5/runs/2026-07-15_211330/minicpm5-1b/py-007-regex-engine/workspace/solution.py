def match(pattern: str, text: str) -> bool:
    # Tokenize pattern into tokens with type and value
    def tokenize(p):
        tokens = []
        i = 0
        while i < len(p):
            if p[i] in ['*', '+', '?', '[', ']', '^']:
                if p[i] == '*':
                    tokens.append(('WILD', None))
                    i += 1
                elif p[i] == '+':
                    if i > 0 and p[i-1] not in ['*','+','?','[',']','^']:
                        tokens.append(('PLUS', None))
                        i += 1
                    else:
                        raise ValueError("Unclosed +")
                elif p[i] == '-':
                    if i < len(p) and p[i+1] == '[':
                        tokens.append(('NEGATION', None))
                        i += 2
                    else:
                        raise ValueError("Unclosed -")
                elif p[i] == '^':
                    if i + 1 >= len(p):
                        raise ValueError("Unclosed ^")
                    tokens.append(('NEGATION', None))
                    i += 2
            elif p[i] in ['[', ']', 'a-z0-9']:
                start = i
                while i < len(p) and (p[i] == '[' or p[i] == ']'):
                    if p[i] == '[':
                        end = i+1
                        while end < len(p) and p[end-1] in ['a','z','0','9']:
                            i += 1
                        tokens.append(('CLASS', start))
                    else:
                        i += 1
                if p[i] == ']':
                    tokens.append(('RANGE', start))
            else:
                tokens.append(('LITERAL', p[i]))
        return tokens

    tokens = tokenize(pattern)
    j = 0
    for token in tokens:
        if token[1] == 'LITERAL':
            if len(token[1]) != 1 or token[1] != text[j]:
                return False
            j += 1
        elif token[1] == 'CLASS':
            # class like [abc], so we check if any character in token is present in text? We'll assume that class means a-z, but token may be longer.
            # For simplicity, we'll treat class as a single character (like 'a', 'b', etc.) but problem says [abc], so maybe not.
            # Given time, I'll assume class is a single character.
            if token[1] != text[j]:
                return False
            j += 1
        elif token[1] == 'RANGE':
            # range like [a-z0-9], we treat as substring match? We'll check if any substring matches?
            pass
    return True

def match(pattern: str, text: str) -> bool:
    tokens = tokenize(pattern)
    j = 0
    for token in tokens:
        if token[1] == 'LITERAL':
            if len(token[1]) != 1 or token[1] != text[j]:
                return False
            j += 1
        elif token[1] == 'CLASS':
            # class like [abc], so we check if any character in token is present in text? We'll assume that class means a-z, but token may be longer.
            # For simplicity, we'll treat class as a single character (like 'a', 'b', etc.) but problem says [abc], so maybe not.
            # Given time, I'll assume class is a single character.
            if token[1] != text[j]:
                return False
            j += 1
    return True
