def match(pattern: str, text: str) -> bool:
    """
    Returns True if pattern matches the entire text.
    Supports regex subset: literal, ., *, +, ?, character classes.
    Raises ValueError for malformed patterns.
    """

    # --- Tokenizer/Parsing ---
    def parse_pattern(s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            # Parse element (literal, ., or class)
            elem = None
            if c == '.':
                elem = '.'
                i += 1
            elif c == '[':
                # Parse character class
                end = s.find(']', i)
                if end == -1:
                    raise ValueError("Unclosed character class")
                class_content = s[i+1:end]
                negated = False
                if class_content and class_content[0] == '^':
                    negated = True
                    class_content = class_content[1:]
                charset = set()
                j = 0
                while j < len(class_content):
                    if class_content[j] == '-' and j > 0 and j < len(class_content)-1:
                        if class_content[j-1] and class_content[j+1]:
                            start_char = class_content[j-1]
                            end_char = class_content[j+1]
                            if ord(start_char) <= ord(end_char):
                                for code in range(ord(start_char), ord(end_char) + 1):
                                    charset.add(chr(code))
                                j += 1 # skip end_char
                            else:
                                charset.add('-')
                        else:
                            charset.add('-')
                    else:
                        charset.add(class_content[j])
                    j += 1
                elem = ('class', charset, negated)
                i = end + 1
            elif c in '*+?':
                raise ValueError(f"Quantifier {c} without preceding element")
            else:
                elem = c
                i += 1

            # Check for quantifier
            quant = ''
            if i < n and s[i] in '*+?':
                quant = s[i]
                i += 1

            tokens.append((elem, quant))
        return tokens

    # --- Element Matching ---
    def elem_matches(elem, char):
        if elem == '.':
            return True
        elif isinstance(elem, tuple) and elem[0] == 'class':
            _, charset, negated = elem
            if negated:
                return char not in charset
            return char in charset
        return elem == char

    # --- Recursive Matching ---
    def backtrack(tokens, idx):
        if not tokens:
            return idx == len(text)

        elem, quant = tokens[0]
        rest_tokens = tokens[1:]

        def try_match(count):
            nonlocal idx
            if idx + count > len(text):
                return False
            for k in range(count):
                if not elem_matches(elem, text[idx + k]):
                    return False
            idx += count
            return True

        if quant == '*':
            # Match 0
            if backtrack(rest_tokens, idx):
                return True
            # Match 1+
            if idx < len(text) and elem_matches(elem, text[idx]):
                if backtrack(tokens, idx + 1):
                    return True
            return False
        elif quant == '+':
            # Match 1+
            if idx < len(text) and elem_matches(elem, text[idx]):
                if backtrack(tokens, idx + 1):
                    return True
            return False
        elif quant == '?':
            # Match 0
            if backtrack(rest_tokens, idx):
                return True
            # Match 1
            if idx < len(text) and elem_matches(elem, text[idx]):
                if backtrack(rest_tokens, idx + 1):
                    return True
            return False
        else:
            # Exact
            if idx < len(text) and elem_matches(elem, text[idx]):
                return backtrack(rest_tokens, idx + 1)
            return False

    tokens = parse_pattern(pattern)
    return backtrack(tokens, 0)
