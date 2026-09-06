import sys

# Increase recursion depth limit for backtracking on longer inputs
sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))


def _parse_pattern(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]
        if ch in "*+?":
            raise ValueError(f"Quantifier '{ch}' with nothing preceding it at index {i}")
        elif ch == ".":
            matcher = lambda c: True
            i += 1
        elif ch == "[":
            closing = pattern.find("]", i + 1)
            if closing == -1:
                raise ValueError(f"Unclosed '[' at index {i}")

            class_str = pattern[i + 1 : closing]
            negated = False
            if class_str.startswith("^"):
                negated = True
                class_str = class_str[1:]

            if not class_str:
                raise ValueError("Empty character class")

            chars = set()
            ranges = []
            k = 0
            length = len(class_str)
            while k < length:
                if k + 2 < length and class_str[k + 1] == "-":
                    c1 = class_str[k]
                    c2 = class_str[k + 2]
                    if ord(c1) > ord(c2):
                        raise ValueError(f"Bad character range '{c1}-{c2}'")
                    ranges.append((ord(c1), ord(c2)))
                    k += 3
                else:
                    chars.add(class_str[k])
                    k += 1

            def make_class_matcher(c_set, r_list, neg):
                def match_char(c):
                    in_class = (c in c_set) or any(lo <= ord(c) <= hi for lo, hi in r_list)
                    return not in_class if neg else in_class

                return match_char

            matcher = make_class_matcher(chars, ranges, negated)
            i = closing + 1
        else:
            lit = ch
            matcher = lambda c, target=lit: c == target
            i += 1

        if i < n and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in "*+?":
                raise ValueError(f"Multiple consecutive quantifiers at index {i}")
        else:
            quant = "one"

        if quant == "+":
            tokens.append((matcher, "one"))
            tokens.append((matcher, "*"))
        else:
            tokens.append((matcher, quant))

    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = _parse_pattern(pattern)
    memo = {}

    def dfs(p_idx: int, t_idx: int) -> bool:
        state = (p_idx, t_idx)
        if state in memo:
            return memo[state]

        if p_idx == len(tokens):
            res = t_idx == len(text)
            memo[state] = res
            return res

        matcher, quant = tokens[p_idx]

        if quant == "one":
            if t_idx < len(text) and matcher(text[t_idx]):
                res = dfs(p_idx + 1, t_idx + 1)
            else:
                res = False
        elif quant == "?":
            res = (
                (t_idx < len(text) and matcher(text[t_idx]) and dfs(p_idx + 1, t_idx + 1))
                or dfs(p_idx + 1, t_idx)
            )
        elif quant == "*":
            res = (
                (t_idx < len(text) and matcher(text[t_idx]) and dfs(p_idx, t_idx + 1))
                or dfs(p_idx + 1, t_idx)
            )
        else:
            res = False

        memo[state] = res
        return res

    return dfs(0, 0)
