def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier with nothing before it")

        if ch == ".":
            predicate = lambda c: True
            i += 1
        elif ch == "[":
            i += 1
            if i >= len(pattern):
                raise ValueError("unclosed character class")

            negated = False
            if pattern[i] == "^":
                negated = True
                i += 1

            chars = set()
            ranges = []
            found_end = False

            while i < len(pattern):
                if pattern[i] == "]":
                    found_end = True
                    i += 1
                    break

                start = pattern[i]
                i += 1

                if i < len(pattern) and pattern[i] == "-":
                    if i + 1 >= len(pattern) or pattern[i + 1] == "]":
                        raise ValueError("invalid character range")
                    end = pattern[i + 1]
                    if start > end:
                        raise ValueError("invalid character range")
                    ranges.append((start, end))
                    i += 2
                else:
                    chars.add(start)

            if not found_end:
                raise ValueError("unclosed character class")
            if not chars and not ranges:
                raise ValueError("empty character class")

            def predicate(c, chars=chars, ranges=ranges, negated=negated):
                contained = c in chars or any(a <= c <= b for a, b in ranges)
                return not contained if negated else contained
        else:
            predicate = lambda c, expected=ch: c == expected
            i += 1

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1
            if i < len(pattern) and pattern[i] in "*+?":
                raise ValueError("multiple quantifiers")

        tokens.append((predicate, quantifier))

    memo = {}

    def matches(token_index: int, text_index: int) -> bool:
        key = (token_index, text_index)
        if key in memo:
            return memo[key]

        if token_index == len(tokens):
            result = text_index == len(text)
        else:
            predicate, quantifier = tokens[token_index]

            if quantifier == "":
                result = (
                    text_index < len(text)
                    and predicate(text[text_index])
                    and matches(token_index + 1, text_index + 1)
                )
            elif quantifier == "?":
                result = matches(token_index + 1, text_index) or (
                    text_index < len(text)
                    and predicate(text[text_index])
                    and matches(token_index + 1, text_index + 1)
                )
            else:
                minimum = 0 if quantifier == "*" else 1
                end = text_index
                while end < len(text) and predicate(text[end]):
                    end += 1

                result = False
                for next_index in range(end, text_index + minimum - 1, -1):
                    if matches(token_index + 1, next_index):
                        result = True
                        break

        memo[key] = result
        return result

    return matches(0, 0)
