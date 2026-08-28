from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in "*+?":
            raise ValueError("quantifier has no preceding element")

        if char == "[":
            i += 1
            negated = i < len(pattern) and pattern[i] == "^"
            if negated:
                i += 1

            entries = []
            while i < len(pattern) and pattern[i] != "]":
                start = pattern[i]

                if (
                    i + 2 < len(pattern)
                    and pattern[i + 1] == "-"
                    and pattern[i + 2] != "]"
                ):
                    end = pattern[i + 2]
                    if ord(start) > ord(end):
                        raise ValueError("invalid character range")
                    entries.append((start, end))
                    i += 3
                else:
                    entries.append((start, start))
                    i += 1

            if i >= len(pattern):
                raise ValueError("unclosed character class")
            if not entries:
                raise ValueError("empty character class")

            element = ("class", (negated, tuple(entries)))
            i += 1
        elif char == ".":
            element = ("dot", None)
            i += 1
        else:
            element = ("literal", char)
            i += 1

        quantifier = None
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((element, quantifier))

    def element_matches(element, char):
        kind, value = element

        if kind == "dot":
            return True
        if kind == "literal":
            return char == value

        negated, entries = value
        contained = any(start <= char <= end for start, end in entries)
        return not contained if negated else contained

    @lru_cache(maxsize=None)
    def backtrack(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        element, quantifier = tokens[token_index]
        consumes = (
            text_index < len(text)
            and element_matches(element, text[text_index])
        )

        if quantifier is None:
            return consumes and backtrack(token_index + 1, text_index + 1)

        if quantifier == "?":
            return (
                backtrack(token_index + 1, text_index)
                or consumes
                and backtrack(token_index + 1, text_index + 1)
            )

        if quantifier == "*":
            return (
                backtrack(token_index + 1, text_index)
                or consumes
                and backtrack(token_index, text_index + 1)
            )

        return consumes and (
            backtrack(token_index + 1, text_index + 1)
            or backtrack(token_index, text_index + 1)
        )

    return backtrack(0, 0)
