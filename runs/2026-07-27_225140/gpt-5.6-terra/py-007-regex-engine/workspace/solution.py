from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier with no preceding element")

        if ch == ".":
            kind = "dot"
            value = None
            i += 1

        elif ch == "[":
            end = pattern.find("]", i + 1)
            if end == -1:
                raise ValueError("unclosed character class")

            content = pattern[i + 1:end]
            negated = content.startswith("^")
            if negated:
                content = content[1:]

            if not content:
                raise ValueError("empty character class")

            ranges = []
            j = 0
            while j < len(content):
                start = content[j]

                if j + 2 < len(content) and content[j + 1] == "-":
                    stop = content[j + 2]
                    if ord(start) > ord(stop):
                        raise ValueError("invalid character range")
                    ranges.append((start, stop))
                    j += 3
                else:
                    ranges.append((start, start))
                    j += 1

            kind = "class"
            value = (tuple(ranges), negated)
            i = end + 1

        else:
            kind = "literal"
            value = ch
            i += 1

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

            if i < len(pattern) and pattern[i] in "*+?":
                raise ValueError("multiple quantifiers on one element")

        tokens.append((kind, value, quantifier))

    def matches_token(token, char):
        kind, value, _ = token

        if kind == "dot":
            return True

        if kind == "literal":
            return char == value

        ranges, negated = value
        included = any(start <= char <= stop for start, stop in ranges)
        return not included if negated else included

    @lru_cache(maxsize=None)
    def search(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        token = tokens[token_index]
        _, _, quantifier = token

        if quantifier == "":
            return (
                text_index < len(text)
                and matches_token(token, text[text_index])
                and search(token_index + 1, text_index + 1)
            )

        if quantifier == "?":
            return (
                search(token_index + 1, text_index)
                or (
                    text_index < len(text)
                    and matches_token(token, text[text_index])
                    and search(token_index + 1, text_index + 1)
                )
            )

        if quantifier == "*":
            return (
                search(token_index + 1, text_index)
                or (
                    text_index < len(text)
                    and matches_token(token, text[text_index])
                    and search(token_index, text_index + 1)
                )
            )

        # quantifier == "+"
        return (
            text_index < len(text)
            and matches_token(token, text[text_index])
            and (
                search(token_index + 1, text_index + 1)
                or search(token_index, text_index + 1)
            )
        )

    return search(0, 0)
