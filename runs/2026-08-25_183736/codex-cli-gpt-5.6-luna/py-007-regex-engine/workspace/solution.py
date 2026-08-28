from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("Quantifier has no preceding element")

        if ch == "[":
            i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed character class")

            negate = False
            if pattern[i] == "^":
                negate = True
                i += 1

            if i >= len(pattern) or pattern[i] == "]":
                raise ValueError("Empty character class")

            entries = []

            while i < len(pattern) and pattern[i] != "]":
                start = pattern[i]
                i += 1

                if i < len(pattern) - 1 and pattern[i] == "-" and pattern[i + 1] != "]":
                    i += 1
                    end = pattern[i]
                    i += 1
                    if start > end:
                        raise ValueError("Invalid character range")
                    entries.append((start, end))
                else:
                    entries.append((start, start))

            if i >= len(pattern) or pattern[i] != "]":
                raise ValueError("Unclosed character class")

            i += 1

            def class_matches(char, entries=entries, negate=negate):
                found = any(start <= char <= end for start, end in entries)
                return not found if negate else found

            atom = class_matches
        elif ch == ".":
            i += 1
            atom = lambda char: True
        else:
            i += 1
            atom = lambda char, expected=ch: char == expected

        minimum, maximum = 1, 1

        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1
            if quantifier == "*":
                minimum, maximum = 0, None
            elif quantifier == "+":
                minimum, maximum = 1, None
            else:
                minimum, maximum = 0, 1

        tokens.append((atom, minimum, maximum))

    @lru_cache(maxsize=None)
    def search(token_index: int, text_index: int) -> bool:
        if token_index == len(tokens):
            return text_index == len(text)

        atom, minimum, maximum = tokens[token_index]
        count = 0
        current = text_index

        while maximum is None or count < maximum:
            if current >= len(text) or not atom(text[current]):
                break
            current += 1
            count += 1

        for repetitions in range(count, minimum - 1, -1):
            if search(token_index + 1, text_index + repetitions):
                return True

        return False

    return search(0, 0)
