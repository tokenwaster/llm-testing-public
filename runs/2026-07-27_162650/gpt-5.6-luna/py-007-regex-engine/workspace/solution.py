def match(pattern: str, text: str) -> bool:
    """Return whether pattern matches the entire text."""

    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier has no preceding element")

        if ch == ".":
            predicate = lambda c: True
            i += 1
        elif ch == "[":
            i += 1
            negated = False

            if i < n and pattern[i] == "^":
                negated = True
                i += 1

            raw = []
            while i < n and pattern[i] != "]":
                raw.append(pattern[i])
                i += 1

            if i >= n:
                raise ValueError("unclosed character class")
            if not raw:
                raise ValueError("empty character class")

            i += 1

            singles = set()
            ranges = []
            j = 0

            while j < len(raw):
                start = raw[j]

                if j + 2 < len(raw) and raw[j + 1] == "-":
                    end = raw[j + 2]
                    if ord(start) > ord(end):
                        raise ValueError("invalid character range")
                    ranges.append((ord(start), ord(end)))
                    j += 3
                else:
                    singles.add(start)
                    j += 1

            def class_predicate(
                c: str,
                singles=singles,
                ranges=ranges,
                negated=negated,
            ) -> bool:
                found = c in singles or any(
                    start <= ord(c) <= end for start, end in ranges
                )
                return not found if negated else found

            predicate = class_predicate
        else:
            literal = ch
            predicate = lambda c, literal=literal: c == literal
            i += 1

        quantifier = ""
        if i < n and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((predicate, quantifier))

    memo = {}

    def match_from(token_index: int, text_index: int) -> bool:
        key = (token_index, text_index)
        if key in memo:
            return memo[key]

        if token_index == len(tokens):
            result = text_index == len(text)
            memo[key] = result
            return result

        predicate, quantifier = tokens[token_index]

        if quantifier == "":
            result = (
                text_index < len(text)
                and predicate(text[text_index])
                and match_from(token_index + 1, text_index + 1)
            )
        elif quantifier == "?":
            result = match_from(token_index + 1, text_index)
            if (
                not result
                and text_index < len(text)
                and predicate(text[text_index])
            ):
                result = match_from(token_index + 1, text_index + 1)
        else:
            minimum = 1 if quantifier == "+" else 0
            maximum = 1 if quantifier == "?" else None

            def repeat(position: int, count: int) -> bool:
                if count >= minimum and match_from(token_index + 1, position):
                    return True

                if (
                    position < len(text)
                    and predicate(text[position])
                    and (maximum is None or count < maximum)
                ):
                    return repeat(position + 1, count + 1)

                return False

            result = repeat(text_index, 0)

        memo[key] = result
        return result

    return match_from(0, 0)
