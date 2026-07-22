from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """Return whether pattern matches the entire text."""

    # Each token is (kind, value, quantifier).
    # kind is "literal", "dot", or "class".
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in "*+?":
            raise ValueError("quantifier has no preceding element")

        if char == "[":
            end = i + 1
            while end < len(pattern) and pattern[end] != "]":
                end += 1
            if end == len(pattern):
                raise ValueError("unclosed character class")

            contents = pattern[i + 1:end]
            negated = contents.startswith("^")
            if negated:
                contents = contents[1:]
            if not contents:
                raise ValueError("empty character class")

            intervals = []
            j = 0
            while j < len(contents):
                if j + 2 < len(contents) and contents[j + 1] == "-":
                    start = contents[j]
                    stop = contents[j + 2]
                    if ord(start) > ord(stop):
                        raise ValueError("invalid character class range")
                    intervals.append((start, stop))
                    j += 3
                else:
                    intervals.append((contents[j], contents[j]))
                    j += 1

            kind = "class"
            value = (negated, tuple(intervals))
            i = end + 1
        elif char == ".":
            kind = "dot"
            value = None
            i += 1
        else:
            kind = "literal"
            value = char
            i += 1

        quantifier = None
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((kind, value, quantifier))

    def element_matches(token, char):
        kind, value, _ = token

        if kind == "dot":
            return True
        if kind == "literal":
            return char == value

        negated, intervals = value
        contained = any(start <= char <= stop for start, stop in intervals)
        return not contained if negated else contained

    @lru_cache(maxsize=None)
    def backtrack(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        token = tokens[token_index]
        quantifier = token[2]

        if quantifier is None:
            return (
                text_index < len(text)
                and element_matches(token, text[text_index])
                and backtrack(token_index + 1, text_index + 1)
            )

        if quantifier == "?":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    text_index < len(text)
                    and element_matches(token, text[text_index])
                    and backtrack(token_index + 1, text_index + 1)
                )
            )

        if quantifier == "*":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    text_index < len(text)
                    and element_matches(token, text[text_index])
                    and backtrack(token_index, text_index + 1)
                )
            )

        # quantifier == "+"
        return (
            text_index < len(text)
            and element_matches(token, text[text_index])
            and (
                backtrack(token_index + 1, text_index + 1)
                or backtrack(token_index, text_index + 1)
            )
        )

    return backtrack(0, 0)
