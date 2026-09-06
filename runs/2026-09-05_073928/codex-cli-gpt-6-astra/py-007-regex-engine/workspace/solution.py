from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in "*+?":
            raise ValueError("Quantifier without a preceding element")

        if char == "[":
            i += 1
            negated = i < len(pattern) and pattern[i] == "^"
            if negated:
                i += 1

            start = i
            while i < len(pattern) and pattern[i] != "]":
                i += 1

            if i == len(pattern):
                raise ValueError("Unclosed character class")
            if i == start:
                raise ValueError("Empty character class")

            members = pattern[start:i]
            singles = set()
            ranges = []
            j = 0

            while j < len(members):
                if j + 2 < len(members) and members[j + 1] == "-":
                    low, high = members[j], members[j + 2]
                    if low > high:
                        raise ValueError("Descending character range")
                    ranges.append((low, high))
                    j += 3
                else:
                    singles.add(members[j])
                    j += 1

            atom = ("class", (negated, frozenset(singles), tuple(ranges)))
            i += 1
        else:
            atom = ("any", None) if char == "." else ("literal", char)
            i += 1

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((atom, quantifier))

    def accepts(atom, char):
        kind, value = atom
        if kind == "any":
            return True
        if kind == "literal":
            return char == value

        negated, singles, ranges = value
        included = char in singles or any(
            low <= char <= high for low, high in ranges
        )
        return not included if negated else included

    @lru_cache(maxsize=None)
    def backtrack(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        atom, quantifier = tokens[token_index]
        consumes = (
            text_index < len(text)
            and accepts(atom, text[text_index])
        )

        if quantifier == "*":
            return backtrack(token_index + 1, text_index) or (
                consumes and backtrack(token_index, text_index + 1)
            )

        if quantifier == "+":
            return consumes and (
                backtrack(token_index + 1, text_index + 1)
                or backtrack(token_index, text_index + 1)
            )

        if quantifier == "?":
            return backtrack(token_index + 1, text_index) or (
                consumes and backtrack(token_index + 1, text_index + 1)
            )

        return consumes and backtrack(token_index + 1, text_index + 1)

    return backtrack(0, 0)
