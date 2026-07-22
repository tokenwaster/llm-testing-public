from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """Return whether pattern matches the entire text."""

    def parse_class(start: int):
        # start points just after '['
        end = pattern.find("]", start)
        if end == -1:
            raise ValueError("unclosed character class")

        content = pattern[start:end]
        if not content:
            raise ValueError("empty character class")

        negated = content.startswith("^")
        if negated:
            content = content[1:]
            if not content:
                raise ValueError("empty character class")

        literals = set()
        ranges = []
        i = 0

        while i < len(content):
            if (
                i + 2 < len(content)
                and content[i + 1] == "-"
            ):
                lower = content[i]
                upper = content[i + 2]
                if ord(lower) > ord(upper):
                    raise ValueError("invalid character class range")
                ranges.append((lower, upper))
                i += 3
            else:
                literals.add(content[i])
                i += 1

        return (negated, frozenset(literals), tuple(ranges)), end + 1

    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier with nothing before it")

        if ch == "[":
            atom, i = parse_class(i + 1)
            kind = "class"
        elif ch == ".":
            atom = None
            kind = "dot"
            i += 1
        else:
            atom = ch
            kind = "literal"
            i += 1

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

            if i < len(pattern) and pattern[i] in "*+?":
                raise ValueError("multiple quantifiers for one element")

        tokens.append((kind, atom, quantifier))

    def atom_matches(kind, atom, char):
        if kind == "dot":
            return True

        if kind == "literal":
            return atom == char

        negated, literals, ranges = atom
        inside = char in literals or any(
            lower <= char <= upper for lower, upper in ranges
        )
        return not inside if negated else inside

    @lru_cache(maxsize=None)
    def search(token_index: int, text_index: int) -> bool:
        if token_index == len(tokens):
            return text_index == len(text)

        kind, atom, quantifier = tokens[token_index]

        def current_matches(index):
            return (
                index < len(text)
                and atom_matches(kind, atom, text[index])
            )

        if quantifier == "":
            return (
                current_matches(text_index)
                and search(token_index + 1, text_index + 1)
            )

        if quantifier == "?":
            return (
                search(token_index + 1, text_index)
                or (
                    current_matches(text_index)
                    and search(token_index + 1, text_index + 1)
                )
            )

        if quantifier == "*":
            index = text_index
            if search(token_index + 1, index):
                return True

            while current_matches(index):
                index += 1
                if search(token_index + 1, index):
                    return True

            return False

        # quantifier == "+"
        if not current_matches(text_index):
            return False

        index = text_index + 1
        if search(token_index + 1, index):
            return True

        while current_matches(index):
            index += 1
            if search(token_index + 1, index):
                return True

        return False

    return search(0, 0)
