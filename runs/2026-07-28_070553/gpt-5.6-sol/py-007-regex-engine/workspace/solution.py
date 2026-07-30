from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """Return whether pattern matches the entire text."""
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in "*+?":
            raise ValueError("quantifier has no preceding element")

        if char == ".":
            kind = "dot"
            value = None
            i += 1

        elif char == "[":
            i += 1
            negated = False

            if i < len(pattern) and pattern[i] == "^":
                negated = True
                i += 1

            class_chars = []
            while i < len(pattern) and pattern[i] != "]":
                class_chars.append(pattern[i])
                i += 1

            if i >= len(pattern):
                raise ValueError("unclosed character class")

            i += 1  # Skip ']'

            literals = set()
            ranges = []
            j = 0

            while j < len(class_chars):
                if j + 2 < len(class_chars) and class_chars[j + 1] == "-":
                    start = class_chars[j]
                    end = class_chars[j + 2]
                    if ord(start) > ord(end):
                        raise ValueError("invalid character range")
                    ranges.append((start, end))
                    j += 3
                else:
                    literals.add(class_chars[j])
                    j += 1

            kind = "class"
            value = (frozenset(literals), tuple(ranges), negated)

        else:
            kind = "literal"
            value = char
            i += 1

        quantifier = None
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((kind, value, quantifier))

    def atom_matches(token, char):
        kind, value, _ = token

        if kind == "dot":
            return True

        if kind == "literal":
            return char == value

        literals, ranges, negated = value
        contained = char in literals or any(
            ord(start) <= ord(char) <= ord(end)
            for start, end in ranges
        )
        return not contained if negated else contained

    @lru_cache(maxsize=None)
    def backtrack(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        token = tokens[token_index]
        quantifier = token[2]
        can_consume = (
            text_index < len(text)
            and atom_matches(token, text[text_index])
        )

        if quantifier is None:
            return can_consume and backtrack(
                token_index + 1, text_index + 1
            )

        if quantifier == "?":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    can_consume
                    and backtrack(token_index + 1, text_index + 1)
                )
            )

        if quantifier == "*":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    can_consume
                    and backtrack(token_index, text_index + 1)
                )
            )

        # quantifier == "+"
        return can_consume and (
            backtrack(token_index + 1, text_index + 1)
            or backtrack(token_index, text_index + 1)
        )

    return backtrack(0, 0)
