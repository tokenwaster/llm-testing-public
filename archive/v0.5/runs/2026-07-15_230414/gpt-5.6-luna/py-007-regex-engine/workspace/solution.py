def match(pattern: str, text: str) -> bool:
    """Return whether pattern matches the entire text."""

    tokens = []
    i = 0
    n = len(pattern)

    def make_class_matcher(chars, ranges, negated):
        chars = frozenset(chars)
        ranges = tuple(ranges)

        def class_matcher(ch):
            found = ch in chars or any(
                ord(start) <= ord(ch) <= ord(end)
                for start, end in ranges
            )
            return not found if negated else found

        return class_matcher

    while i < n:
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier has no preceding element")

        if ch == ".":
            matcher = lambda _: True
            i += 1
        elif ch == "[":
            i += 1
            negated = False

            if i < n and pattern[i] == "^":
                negated = True
                i += 1

            if i >= n or pattern[i] == "]":
                raise ValueError("empty or malformed character class")

            chars = []
            ranges = []
            closed = False

            while i < n:
                current = pattern[i]

                if current == "]":
                    closed = True
                    i += 1
                    break

                i += 1

                if current == "-":
                    chars.append(current)
                    continue

                if i + 1 < n and pattern[i] == "-" and pattern[i + 1] != "]":
                    start = current
                    end = pattern[i + 1]

                    if start > end:
                        raise ValueError("invalid character range")

                    ranges.append((start, end))
                    i += 2
                else:
                    chars.append(current)

            if not closed:
                raise ValueError("unclosed character class")

            matcher = make_class_matcher(chars, ranges, negated)
        else:
            matcher = lambda value, expected=ch: value == expected
            i += 1

        quantifier = ""
        if i < n and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((matcher, quantifier))

    def match_from(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        matcher, quantifier = tokens[token_index]
        positions = [text_index]
        current = text_index

        while current < len(text) and matcher(text[current]):
            current += 1
            positions.append(current)

        if quantifier == "":
            if len(positions) == 1:
                return False
            return match_from(token_index + 1, positions[1])

        if quantifier == "?":
            return (
                match_from(token_index + 1, text_index)
                or (
                    len(positions) > 1
                    and match_from(token_index + 1, positions[1])
                )
            )

        if quantifier == "+":
            if len(positions) == 1:
                return False
            candidates = positions[1:]
        else:  # "*"
            candidates = positions

        for position in reversed(candidates):
            if match_from(token_index + 1, position):
                return True

        return False

    return match_from(0, 0)
