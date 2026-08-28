from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier has nothing before it")

        if ch == ".":
            atom = ("any",)
            i += 1
        elif ch == "[":
            i += 1
            negated = False
            if i < len(pattern) and pattern[i] == "^":
                negated = True
                i += 1

            content_start = i
            while i < len(pattern) and pattern[i] != "]":
                i += 1
            if i == len(pattern):
                raise ValueError("unclosed character class")

            content = pattern[content_start:i]
            i += 1

            chars = set()
            j = 0
            while j < len(content):
                if j + 2 < len(content) and content[j + 1] == "-":
                    start, end = content[j], content[j + 2]
                    if start > end:
                        raise ValueError("invalid character range")
                    chars.update(chr(code) for code in range(ord(start), ord(end) + 1))
                    j += 3
                else:
                    chars.add(content[j])
                    j += 1

            atom = ("class", frozenset(chars), negated)
        else:
            atom = ("literal", ch)
            i += 1

        quantifier = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((atom, quantifier))

    def atom_matches(atom, char):
        kind = atom[0]
        if kind == "any":
            return True
        if kind == "literal":
            return char == atom[1]
        allowed, negated = atom[1], atom[2]
        return (char not in allowed) if negated else (char in allowed)

    @lru_cache(maxsize=None)
    def search(token_index, text_index):
        if token_index == len(tokens):
            return text_index == len(text)

        atom, quantifier = tokens[token_index]

        if quantifier == "":
            return (
                text_index < len(text)
                and atom_matches(atom, text[text_index])
                and search(token_index + 1, text_index + 1)
            )

        minimum = 1 if quantifier == "+" else 0
        end = text_index
        while end < len(text) and atom_matches(atom, text[end]):
            end += 1

        for next_index in range(end, text_index + minimum - 1, -1):
            if search(token_index + 1, next_index):
                return True
        return False

    return search(0, 0)
