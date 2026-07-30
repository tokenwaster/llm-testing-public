def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("Quantifier has no preceding element")

        if ch == "[":
            start = i
            i += 1
            negated = False

            if i < len(pattern) and pattern[i] == "^":
                negated = True
                i += 1

            members = set()
            found_closing = False

            while i < len(pattern):
                if pattern[i] == "]":
                    found_closing = True
                    i += 1
                    break

                first = pattern[i]
                i += 1

                if (
                    first != "-"
                    and i + 1 < len(pattern)
                    and pattern[i] == "-"
                    and pattern[i + 1] != "]"
                ):
                    last = pattern[i + 1]
                    if ord(first) > ord(last):
                        raise ValueError("Invalid character range")
                    members.update(chr(code) for code in range(ord(first), ord(last) + 1))
                    i += 2
                else:
                    members.add(first)

            if not found_closing or not members:
                raise ValueError("Malformed character class")

            if negated:
                predicate = lambda c, members=members: c not in members
            else:
                predicate = lambda c, members=members: c in members

        elif ch == ".":
            i += 1
            predicate = lambda c: True

        else:
            i += 1
            predicate = lambda c, expected=ch: c == expected

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((predicate, quantifier))

    def search(token_index: int, text_index: int) -> bool:
        if token_index == len(tokens):
            return text_index == len(text)

        predicate, quantifier = tokens[token_index]

        if quantifier == "":
            return (
                text_index < len(text)
                and predicate(text[text_index])
                and search(token_index + 1, text_index + 1)
            )

        if quantifier == "?":
            return search(token_index + 1, text_index) or (
                text_index < len(text)
                and predicate(text[text_index])
                and search(token_index + 1, text_index + 1)
            )

        if quantifier == "*":
            return search(token_index + 1, text_index) or (
                text_index < len(text)
                and predicate(text[text_index])
                and search(token_index, text_index + 1)
            )

        if quantifier == "+":
            return (
                text_index < len(text)
                and predicate(text[text_index])
                and (
                    search(token_index + 1, text_index + 1)
                    or search(token_index, text_index + 1)
                )
            )

        raise ValueError("Unknown quantifier")

    return search(0, 0)
