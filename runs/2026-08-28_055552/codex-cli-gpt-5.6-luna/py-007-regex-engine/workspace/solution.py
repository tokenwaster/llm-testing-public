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

            if i >= len(pattern) or pattern[i] == "]":
                raise ValueError("Empty character class")

            items = []
            while i < len(pattern) and pattern[i] != "]":
                first = pattern[i]
                i += 1

                if i < len(pattern) - 1 and pattern[i] == "-" and pattern[i + 1] != "]":
                    i += 1
                    last = pattern[i]
                    i += 1
                    if first > last:
                        raise ValueError("Invalid character range")
                    items.append(("range", first, last))
                else:
                    items.append(("char", first))

            if i >= len(pattern) or pattern[i] != "]":
                raise ValueError("Unclosed character class")

            i += 1
            atom = ("class", negated, items)
        elif ch == ".":
            i += 1
            atom = ("dot",)
        else:
            i += 1
            atom = ("literal", ch)

        quant = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1

        tokens.append((atom, quant))

    def matches_atom(atom, ch):
        kind = atom[0]

        if kind == "dot":
            return True
        if kind == "literal":
            return ch == atom[1]

        _, negated, items = atom
        found = any(
            (item[1] <= ch <= item[2]) if item[0] == "range"
            else ch == item[1]
            for item in items
        )
        return not found if negated else found

    memo = {}

    def visit(token_index, text_index):
        key = (token_index, text_index)
        if key in memo:
            return memo[key]

        if token_index == len(tokens):
            result = text_index == len(text)
            memo[key] = result
            return result

        atom, quant = tokens[token_index]

        if quant == "":
            result = (
                text_index < len(text)
                and matches_atom(atom, text[text_index])
                and visit(token_index + 1, text_index + 1)
            )
        elif quant == "?":
            result = visit(token_index + 1, text_index) or (
                text_index < len(text)
                and matches_atom(atom, text[text_index])
                and visit(token_index + 1, text_index + 1)
            )
        elif quant == "*":
            result = visit(token_index + 1, text_index) or (
                text_index < len(text)
                and matches_atom(atom, text[text_index])
                and visit(token_index, text_index + 1)
            )
        else:  # "+"
            result = (
                text_index < len(text)
                and matches_atom(atom, text[text_index])
                and (
                    visit(token_index + 1, text_index + 1)
                    or visit(token_index, text_index + 1)
                )
            )

        memo[key] = result
        return result

    return visit(0, 0)
