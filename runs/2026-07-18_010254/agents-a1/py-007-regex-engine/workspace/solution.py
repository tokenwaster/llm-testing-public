from functools import lru_cache

def match(pattern: str, text: str) -> bool:
    # Parse pattern into elements
    elements = []  # each element: [type, value, negated, quantifier]
    i = 0
    n = len(pattern)
    
    def parse_class_content(content):
        chars = set()
        idx = 0
        length = len(content)
        while idx < length:
            if idx + 2 < length and content[idx+1] == '-':
                start_char = content[idx]
                end_char = content[idx+2]
                if ord(start_char) > ord(end_char):
                    raise ValueError("Invalid character range")
                for code in range(ord(start_char), ord(end_char)+1):
                    chars.add(chr(code))
                idx += 3
            else:
                ch = content[idx]
                chars.add(ch)
                idx += 1
        return chars

    while i < n:
        c = pattern[i]
        if c == '.':
            elements.append(['dot', None, False, None])
            i += 1
        elif c == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            k = j
            while k < n and pattern[k] != ']':
                k += 1
            if k >= n:
                raise ValueError("Unclosed character class")
            content = pattern[j:k]
            if not content:
                raise ValueError("Empty character class")
            try:
                char_set = parse_class_content(content)
            except Exception as e:
                raise ValueError(str(e))
            elements.append(['class', char_set, negated, None])
            i = k + 1
        elif c in '*+?':
            if not elements:
                raise ValueError(f"Invalid pattern: '{c}' with nothing before it")
            last = elements[-1]
            if last[3] is not None:
                raise ValueError("Invalid pattern: multiple quantifiers on same element")
            last[3] = c
            i += 1
        else:
            elements.append(['char', c, False, None])
            i += 1

    @lru_cache(maxsize=None)
    def dp(i, j):
        if j == len(elements):
            return i == len(text)
        elem = elements[j]
        typ, val, neg, quant = elem[0], elem[1], elem[2], elem[3]

        def matches_char(ch):
            if typ == 'char':
                return ch == val
            elif typ == 'dot':
                return True
            elif typ == 'class':
                if neg:
                    return ch not in val
                else:
                    return ch in val
            return False

        if quant is None:
            if i < len(text) and matches_char(text[i]):
                return dp(i+1, j+1)
            return False

        elif quant == '*':
            k = 0
            while True:
                if dp(i+k, j+1):
                    return True
                if i+k >= len(text) or not matches_char(text[i+k]):
                    break
                k += 1
            return False

        elif quant == '+':
            if i >= len(text) or not matches_char(text[i]):
                return False
            k = 0
            while True:
                if dp(i+1+k, j+1):
                    return True
                if i+1+k >= len(text) or not matches_char(text[i+1+k]):
                    break
                k += 1
            return False

        elif quant == '?':
            if dp(i, j+1):
                return True
            if i < len(text) and matches_char(text[i]):
                return dp(i+1, j+1)
            return False

    return dp(0, 0)
