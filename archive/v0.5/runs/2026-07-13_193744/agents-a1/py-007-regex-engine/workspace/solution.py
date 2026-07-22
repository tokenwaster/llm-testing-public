def match(pattern: str, text: str) -> bool:
    """
    Matches pattern against entire text using recursive backtracking.
    Supports: literals, '.', '*', '+', '?', and character classes [abc], [a-z], [^abc].
    Raises ValueError for malformed patterns (unclosed '[', quantifier without preceding element).
    """
    # Parse pattern into elements: each element is (type, value, quantifier)
    # type: 'char', 'dot', 'class'
    # value: for 'char' -> the character; for 'dot' -> None; for 'class' -> class string
    # quantifier: None, '*', '+', '?'
    elements = []
    i = 0
    n = len(pattern)

    while i < n:
        if pattern[i] == '[':
            j = i + 1
            while j < n and pattern[j] != ']':
                j += 1
            if j >= n:
                raise ValueError("Unclosed character class")
            class_str = pattern[i+1:j]
            i = j + 1
            quantifier = None
            if i < n and pattern[i] in '*?+':
                quantifier = pattern[i]
                i += 1
            elements.append(('class', class_str, quantifier))
        elif pattern[i] == '.':
            i += 1
            quantifier = None
            if i < n and pattern[i] in '*?+':
                quantifier = pattern[i]
                i += 1
            elements.append(('dot', None, quantifier))
        elif pattern[i] in '*?+':
            raise ValueError("Invalid quantifier at position {}".format(i))
        else:
            ch = pattern[i]
            i += 1
            quantifier = None
            if i < n and pattern[i] in '*?+':
                quantifier = pattern[i]
                i += 1
            elements.append(('char', ch, quantifier))

    # Helper: check if character c is in class_str (supports ranges and negation)
    def is_in_class(c: str, class_str: str) -> bool:
        if not class_str:
            return False
        negated = False
        start_idx = 0
        if class_str[0] == '^':
            negated = True
            start_idx = 1
        chars = set()
        idx = start_idx
        while idx < len(class_str):
            # Check for range: char '-' next_char (must have two characters after)
            if idx + 2 < len(class_str) and class_str[idx+1] == '-':
                lo = class_str[idx]
                hi = class_str[idx+2]
                for code in range(ord(lo), ord(hi)+1):
                    chars.add(chr(code))
                idx += 3
            else:
                chars.add(class_str[idx])
                idx += 1
        if negated:
            return c not in chars
        else:
            return c in chars

    # Memoization table for DP states (i_idx, j_idx)
    memo = {}

    def dp(i_idx: int, j_idx: int) -> bool:
        key = (i_idx, j_idx)
        if key in memo:
            return memo[key]

        # Base case: pattern exhausted
        if i_idx == len(elements):
            res = (j_idx == len(text))
            memo[key] = res
            return res

        typ, val, quant = elements[i_idx]
        can_match = False
        if j_idx < len(text):
            if typ == 'char':
                if text[j_idx] == val:
                    can_match = True
            elif typ == 'dot':
                can_match = True
            elif typ == 'class':
                if is_in_class(text[j_idx], val):
                    can_match = True

        if quant is None:
            res = can_match and dp(i_idx + 1, j_idx + 1)
        elif quant == '?':
            # Skip this element OR match one occurrence
            res = dp(i_idx + 1, j_idx)  # skip
            if not res and can_match:
                res = dp(i_idx + 1, j_idx + 1)
        elif quant == '*':
            # Skip this element entirely OR consume one char and stay on same element
            res = dp(i_idx + 1, j_idx)  # skip (zero occurrences)
            if not res and can_match:
                res = dp(i_idx, j_idx + 1)  # consume one and try again
        elif quant == '+':
            # Must match at least one occurrence
            if can_match:
                res = dp(i_idx + 1, j_idx + 1) or dp(i_idx, j_idx + 1)
            else:
                res = False
        else:
            raise ValueError("Unknown quantifier")

        memo[key] = res
        return res

    return dp(0, 0)
