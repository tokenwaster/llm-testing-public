def match(pattern: str, text: str) -> bool:
    """
    Reports whether 'pattern' matches the ENTIRE 'text', supporting a subset of regex.
    Supports literal characters, '.', '*', '+', '?', and character classes like [abc], 
    [a-z0-9], and [^abc].
    """

    class Token:
        def __init__(self, matcher_func, quantifier=None):
            self.matcher = matcher_func
            self.quantifier = quantifier

    def parse_class(pattern, start_idx):
        # pattern[start_idx] is '['
        i = start_idx + 1
        negate = False
        if i < len(pattern) and pattern[i] == '^':
            negate = True
            i += 1
        
        content = []
        while i < len(pattern) and pattern[i] != ']':
            content.append(pattern[i])
            i += 1
        
        if i >= len(pattern):
            raise ValueError("Unclosed bracket")
        
        allowed = set()
        j = 0
        while j < len(content):
            # A hyphen is a range if it's not at the start or end of the content.
            if content[j] == '-' and j > 0 and j < len(content) - 1:
                start_char = content[j-1]
                end_char = content[j+1]
                if ord(start_char) > ord(end_char):
                    raise ValueError("Invalid range")
                for code in range(ord(start_char), ord(end_char) + 1):
                    allowed.add(chr(code))
                j += 2
            else:
                allowed.add(content[j])
                j += 1
        
        def matcher(c):
            res = c in allowed
            return not res if negate else res
        
        return matcher, i + 1

    tokens = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char in '*+?':
            raise ValueError("Quantifier without preceding element")
        
        matcher_func = None
        if char == '.':
            matcher_func = lambda c: True
            i += 1
        elif char == '[':
            matcher_func, i = parse_class(pattern, i)
        else:
            # Literal character
            matcher_func = lambda c: c == char
            i += 1
        
        if i < len(pattern) and pattern[i] in '*+?':
            quantifier = pattern[i]
            i += 1
            tokens.append(Token(matcher_func, quantifier))
            # Check for consecutive quantifiers like ** or *+
            if i < len(pattern) and pattern[i] in '*+?':
                raise ValueError("Consecutive quantifiers")
        else:
            tokens.append(Token(matcher_func, None))

    memo = {}

    def solve(token_idx, text_idx):
        state = (token_idx, text_idx)
        if state in memo:
            return memo[state]
        
        # Base case: all tokens processed
        if token_idx == len(tokens):
            res = (text_idx == len(text))
            memo[state] = res
            return res
        
        token = tokens[token_idx]
        res = False
        
        if token.quantifier is None:
            # Match exactly one character
            if text_idx < len(text) and token.matcher(text[text_idx]):
                res = solve(token_idx + 1, text_idx + 1)
            else:
                res = False
        elif token.quantifier == '?':
            # Option 1: Skip the token (zero occurrences)
            if solve(token_idx + 1, text_idx):
                res = True
            # Option 2: Match exactly one character and move to next token
            elif text_idx < len(text) and token.matcher(text[text_idx]):
                res = solve(token_idx + 1, text_idx + 1)
        elif token.quantifier == '*':
            # Option 1: Skip the token (zero occurrences)
            if solve(token_idx + 1, text_idx):
                res = True
            # Option 2: Match one character and stay on this token to potentially match more
            elif text_idx < len(text) and token.matcher(text[text_idx]):
                res = solve(token_idx, text_idx + 1)
        elif token.quantifier == '+':
            # Must match at least one character
            if text_idx < len(text) and token.matcher(text[text_idx]):
                # After matching the first required character, it behaves like '*'
                # (either move to next token or stay on this one to match more)
                res = solve(token_idx + 1, text_idx + 1) or solve(token_idx, text_idx + 1)
            else:
                res = False
        
        memo[state] = res
        return res

    return solve(0, 0)
