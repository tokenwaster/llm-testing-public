from functools import lru_cache
from typing import Optional


def match(pattern: str, text: str) -> bool:
    tokens = []
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char in "*+?":
            raise ValueError("quantifier has no preceding element")

        if char == "[":
            i += 1
            if i >= len(pattern):
                raise ValueError("unclosed character class")

            negated = False
            if pattern[i] == "^":
                negated = True
                i += 1

            members = []
            while i < len(pattern) and pattern[i] != "]":
                start = pattern[i]

                if (
                    i + 2 < len(pattern)
                    and pattern[i + 1] == "-"
                    and pattern[i + 2] != "]"
                ):
                    end = pattern[i + 2]
                    if ord(start) > ord(end):
                        raise ValueError("invalid character range")
                    members.append((start, end))
                    i += 3
                else:
                    members.append((start, start))
                    i += 1

            if i >= len(pattern):
                raise ValueError("unclosed character class")
            if not members:
                raise ValueError("empty character class")

            atom = ("class", (negated, tuple(members)))
            i += 1
        elif char == ".":
            atom = ("dot", None)
            i += 1
        else:
            atom = ("literal", char)
            i += 1

        quantifier: Optional[str] = None
        if i < len(pattern) and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1
            if i < len(pattern) and pattern[i] in "*+?":
                raise ValueError("multiple quantifiers on one element")

        tokens.append((atom, quantifier))

    def atom_matches(atom, char: str) -> bool:
        kind, value = atom

        if kind == "dot":
            return True
        if kind == "literal":
            return char == value

        negated, ranges = value
        contained = any(start <= char <= end for start, end in ranges)
        return not contained if negated else contained

    @lru_cache(maxsize=None)
    def backtrack(token_index: int, text_index: int) -> bool:
        if token_index == len(tokens):
            return text_index == len(text)

        atom, quantifier = tokens[token_index]
        consumes = (
            text_index < len(text)
            and atom_matches(atom, text[text_index])
        )

        if quantifier is None:
            return consumes and backtrack(token_index + 1, text_index + 1)

        if quantifier == "?":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    consumes
                    and backtrack(token_index + 1, text_index + 1)
                )
            )

        if quantifier == "*":
            return (
                backtrack(token_index + 1, text_index)
                or (
                    consumes
                    and backtrack(token_index, text_index + 1)
                )
            )

        return consumes and (
            backtrack(token_index + 1, text_index + 1)
            or backtrack(token_index, text_index + 1)
        )

    return backtrack(0, 0)
