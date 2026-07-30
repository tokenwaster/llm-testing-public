class Token:
    def __init__(self, token_type, value=None, negated=False):
        self.type = token_type  # 'literal', 'dot', 'class'
        self.value = value      # character, or set of characters
        self.negated = negated
        self.quantifier = None  # None, '*', '+', '?'

def parse_pattern(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        char = pattern[i]
        if char == '[':
            # start of character class
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
            
            class_content = []
            while i < n and pattern[i] != ']':
                class_content.append(pattern[i])
                i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            
            i += 1  # consume ']'
            
            if not class_content:
                raise ValueError("Empty character class")
                
            allowed_chars = set()
            j = 0
            m = len(class_content)
            while j < m:
                if j + 2 < m and class_content[j+1] == '-':
                    start_char = class_content[j]
                    end_char = class_content[j+2]
                    if start_char > end_char:
                        raise ValueError("Invalid range in character class")
                    for c in range(ord(start_char), ord(end_char) + 1):
                        allowed_chars.add(chr(c))
                    j += 3
                else:
                    allowed_chars.add(class_content[j])
                    j += 1
            
            tokens.append(Token('class', value=allowed_chars, negated=negated))
            
        elif char == ']':
            raise ValueError("Unmatched ]")
        elif char in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{char}' without preceding element")
        elif char == '.':
            tokens.append(Token('dot'))
            i += 1
        else:
            tokens.append(Token('literal', value=char))
            i += 1
            
        # Check if the next character is a quantifier
        if i < n and pattern[i] in ('*', '+', '?'):
            tokens[-1].quantifier = pattern[i]
            i += 1
            
    return tokens

def token_matches(token, char):
    if token.type == 'literal':
        return token.value == char
    elif token.type == 'dot':
        return True
    elif token.type == 'class':
        is_in = char in token.value
        return not is_in if token.negated else is_in
    return False

def match(pattern: str, text: str) -> bool:
    tokens = parse_pattern(pattern)
    memo = {}
    
    def match_from(token_idx, text_idx):
        state = (token_idx, text_idx)
        if state in memo:
            return memo[state]
            
        if token_idx == len(tokens):
            res = (text_idx == len(text))
            memo[state] = res
            return res
            
        token = tokens[token_idx]
        
        if token.quantifier == '*':
            # Try 0 matches first
            if match_from(token_idx + 1, text_idx):
                memo[state] = True
                return True
            # Try 1 or more matches
            curr_idx = text_idx
            while curr_idx < len(text) and token_matches(token, text[curr_idx]):
                curr_idx += 1
                if match_from(token_idx + 1, curr_idx):
                    memo[state] = True
                    return True
            memo[state] = False
            return False
            
        elif token.quantifier == '+':
            # Try 1 or more matches
            curr_idx = text_idx
            while curr_idx < len(text) and token_matches(token, text[curr_idx]):
                curr_idx += 1
                if match_from(token_idx + 1, curr_idx):
                    memo[state] = True
                    return True
            memo[state] = False
            return False
            
        elif token.quantifier == '?':
            # Try 0 matches
            if match_from(token_idx + 1, text_idx):
                memo[state] = True
                return True
            # Try 1 match
            if text_idx < len(text) and token_matches(token, text[text_idx]):
                if match_from(token_idx + 1, text_idx + 1):
                    memo[state] = True
                    return True
            memo[state] = False
            return False
            
        else:
            # Exactly 1 match
            if text_idx < len(text) and token_matches(token, text[text_idx]):
                res = match_from(token_idx + 1, text_idx + 1)
                memo[state] = res
                return res
            memo[state] = False
            return False

    return match_from(0, 0)
