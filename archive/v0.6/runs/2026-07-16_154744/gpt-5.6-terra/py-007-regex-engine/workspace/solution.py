from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """
    Return True if pattern matches the entire text.

    Supported syntax:
      .        any character
      *        zero or more of preceding element
      +        one or more of preceding element
      ?        zero or one of preceding element
      [abc]    character class
      [a-z]    character range
      [^abc]  negated character class
    """

    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier has nothing to repeat")

        if ch == ".":
            kind = "any"
            value = None
            i += 1

        elif ch == "[":
            i += 1
            if i >= len(pattern):
                raise ValueError("unclosed character class")

            negated = False
            if pattern[i] == "^":
                negated = True
                i += 1

            class_body = []
            while i < len(pattern) and pattern[i] != "]":
                class_body.append(pattern[i])
                i += 1

            if i >= len(pattern):
                raise ValueError("unclosed character class")

            if not class_body:
                raise ValueError("empty character class")

            i += 1  # Skip closing ']'

            ranges = []
            j = 0
            while j < len(class_body):
                if (
                    j + 2 < len(class_body)
                    and class_body[j + 1] == "-"
                ):
                    start = class_body[j]
                    end = class_body[j + 2]
                    if start > end:
                        raise ValueError("invalid character class range")
                    ranges.append((start, end))
                    j += 3
                else:
                    ranges.append((class_body[j], class_body[j]))
                    j += 1

            kind = "class"
            value = (negated, tuple(ranges))

        else:
            kind = "literal"
            value = ch
            i += 1

        minimum = 1
        maximum = 1

        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

            if quantifier == "*":
                minimum = 0
                maximum = None
            elif quantifier == "+":
                minimum = 1
                maximum = None
            else:
                minimum = 0
                maximum = 1

        tokens.append((kind, value, minimum, maximum))

    def token_matches(token, char):
        kind, value, _, _ = token

        if kind == "any":
            return True

        if kind == "literal":
            return char == value

        negated, ranges = value
        found = any(start <= char <= end for start, end in ranges)
        return not found if negated else found

    @lru_cache(maxsize=None)
    def matches_from(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        token = tokens[token_index]
        _, _, minimum, maximum = token

        position = text_index

        for _ in range(minimum):
            if position >= len(text) or not token_matches(token, text[position]):
                return False
            position += 1

        count = minimum
        while True:
            if matches_from(token_index + 1, position):
                return True

            if maximum is not None and count >= maximum:
                return False

            if position >= len(text) or not token_matches(token, text[position]):
                return False

            position += 1
            count += 1

    return matches_from(0, 0)
