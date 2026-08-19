import sys

sys.setrecursionlimit(50000)


def _parse_pattern(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        char = pattern[i]

        if char in "*+?":
            raise ValueError(f"Quantifier '{char}' with no preceding element")

        if char == ".":
            matcher = lambda c: True
            i += 1
        elif char == "[":
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")

            negated = False
            if pattern[i] == "^":
                negated = True
                i += 1
                if i >= n:
                    raise ValueError("Unclosed character class")

            class_chars = []
            closed = False
            while i < n:
                if pattern[i] == "]":
                    closed = True
                    i += 1
                    break
                class_chars.append(pattern[i])
                i += 1

            if not closed:
                raise ValueError("Unclosed character class")
            if not class_chars:
                raise ValueError("Empty character class")

            char_set = set()
            j = 0
            m = len(class_chars)
            while j < m:
                if j + 2 < m and class_chars[j + 1] == "-":
                    start_c = class_chars[j]
                    end_c = class_chars[j + 2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError(f"Invalid range in character class: {start_c}-{end_c}")
                    for code in range(ord(start_c), ord(end_c) + 1):
                        char_set.add(chr(code))
                    j += 3
                else:
                    char_set.add(class_chars[j])
                    j += 1

            if negated:
                matcher = (lambda s: lambda c: c not in s)(char_set)
            else:
                matcher = (lambda s: lambda c: c in s)(char_set)
        else:
            matcher = (lambda target: lambda c: c == target)(char)
            i += 1

        quantifier = "1"
        if i < n and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1
            if i < n and pattern[i] in "*+?":
                raise ValueError("Multiple quantifiers applied to single element")

        tokens.append((matcher, quantifier))

    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)
    memo = {}

    def match_from(t_idx: int, s_idx: int) -> bool:
        state = (t_idx, s_idx)
        if state in memo:
            return memo[state]

        if t_idx == len(tokens):
            res = s_idx == len(text)
            memo[state] = res
            return res

        matcher, quant = tokens[t_idx]

        if quant == "1":
            if s_idx < len(text) and matcher(text[s_idx]):
                res = match_from(t_idx + 1, s_idx + 1)
            else:
                res = False
        elif quant == "?":
            if match_from(t_idx + 1, s_idx):
                res = True
            elif s_idx < len(text) and matcher(text[s_idx]) and match_from(t_idx + 1, s_idx + 1):
                res = True
            else:
                res = False
        elif quant == "*":
            if match_from(t_idx + 1, s_idx):
                res = True
            elif s_idx < len(text) and matcher(text[s_idx]) and match_from(t_idx, s_idx + 1):
                res = True
            else:
                res = False
        elif quant == "+":
            if s_idx < len(text) and matcher(text[s_idx]):
                res = match_from(t_idx + 1, s_idx + 1) or match_from(t_idx, s_idx + 1)
            else:
                res = False

        memo[state] = res
        return res

    return match_from(0, 0)
