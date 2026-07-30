def match(pattern: str, text: str) -> bool:
    atoms = []
    quantifiers = {"*", "+", "?"}
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in quantifiers:
            raise ValueError("quantifier has no preceding element")

        if char == "[":
            end = pattern.find("]", i + 1)
            if end == -1:
                raise ValueError("unclosed character class")

            j = i + 1
            negated = False
            if j < end and pattern[j] == "^":
                negated = True
                j += 1

            if j == end:
                raise ValueError("empty character class")

            singles = set()
            ranges = []

            while j < end:
                if j + 2 < end and pattern[j + 1] == "-":
                    start_char = pattern[j]
                    end_char = pattern[j + 2]
                    if ord(start_char) > ord(end_char):
                        raise ValueError("invalid character range")
                    ranges.append((start_char, end_char))
                    j += 3
                else:
                    singles.add(pattern[j])
                    j += 1

            atom = ("class", (negated, frozenset(singles), tuple(ranges)))
            i = end + 1
        elif char == ".":
            atom = ("any", None)
            i += 1
        else:
            atom = ("literal", char)
            i += 1

        quantifier = None
        if i < len(pattern) and pattern[i] in quantifiers:
            quantifier = pattern[i]
            i += 1

        atoms.append((atom, quantifier))

    def matches_atom(atom, char):
        kind, value = atom

        if kind == "any":
            return True
        if kind == "literal":
            return char == value

        negated, singles, ranges = value
        contained = char in singles or any(
            start <= char <= end for start, end in ranges
        )
        return not contained if negated else contained

    positions = {0}
    text_length = len(text)

    for atom, quantifier in atoms:
        if quantifier is None:
            positions = {
                pos + 1
                for pos in positions
                if pos < text_length and matches_atom(atom, text[pos])
            }

        elif quantifier == "?":
            new_positions = set(positions)
            new_positions.update(
                pos + 1
                for pos in positions
                if pos < text_length and matches_atom(atom, text[pos])
            )
            positions = new_positions

        elif quantifier == "*":
            new_positions = set(positions)
            for pos in range(text_length):
                if pos in new_positions and matches_atom(atom, text[pos]):
                    new_positions.add(pos + 1)
            positions = new_positions

        else:  # "+"
            new_positions = {
                pos + 1
                for pos in positions
                if pos < text_length and matches_atom(atom, text[pos])
            }
            for pos in range(text_length):
                if pos in new_positions and matches_atom(atom, text[pos]):
                    new_positions.add(pos + 1)
            positions = new_positions

        if not positions:
            return False

    return text_length in positions
