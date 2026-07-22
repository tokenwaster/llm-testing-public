from functools import lru_cache


def _parse_class(pattern: str, i: int):
    """Parse a character class starting at pattern[i] == '['."""
    n = len(pattern)
    if pattern[i] != "[":
        raise ValueError("Expected '['")
    i += 1

    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1

    chars = set()

    # Empty class "[]" or "[^]"
    if i < n and pattern[i] == "]":
        i += 1
    else:
        while i < n and pattern[i] != "]":
            ch = pattern[i]
            # Leading/trailing '-' is a literal hyphen
            if ch == "-":
                chars.add("-")
                i += 1
                continue

            # Range like a-z
            if (
                i + 2 < n
                and pattern[i + 1] == "-"
                and pattern[i + 2] != "]"
            ):
                start = pattern[i]
                end = pattern[i + 2]
                if ord(start) > ord(end):
                    raise ValueError(
                        f"Invalid character range [{start}-{end}]"
                    )
                for code in range(ord(start), ord(end) + 1):
                    chars.add(chr(code))
                i += 3
            else:
                chars.add(ch)
                i += 1

    if i >= n:
        raise ValueError("Unclosed character class")

    i += 1  # skip closing ']'
    return ("class", chars, negated), i


def _parse(pattern: str):
    """Parse the pattern into a list of (atom, quantifier) tokens."""
    n = len(pattern)
    tokens = []
    i = 0

    while i < n:
        ch = pattern[i]

        if ch == "[":
            atom, i = _parse_class(pattern, i)
        elif ch == ".":
            atom = ("dot",)
            i += 1
        else:
            if ch in "*+?":
                raise ValueError(
                    f"Quantifier '{ch}' has no preceding element"
                )
            atom = ("char", ch)
            i += 1

        quantifier = None
        if i < n and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

        tokens.append((atom, quantifier))

    return tokens


def _atom_matches(atom, ch: str) -> bool:
    """Return whether a single character matches an unquantified atom."""
    kind = atom[0]
    if kind == "dot":
        return True
    if kind == "char":
        return atom[1] == ch
    # kind == "class"
    _, chars, negated = atom
    in_set = ch in chars
    return not in_set if negated else in_set


def match(pattern: str, text: str) -> bool:
    """Return True iff pattern matches the entire text."""
    tokens = _parse(pattern)
    text_len = len(text)

    @lru_cache(maxsize=None)
    def dfs(idx: int, pos: int) -> bool:
        if idx == len(tokens):
            return pos == text_len

        atom, quant = tokens[idx]

        if quant is None:
            if pos < text_len and _atom_matches(atom, text[pos]):
                return dfs(idx + 1, pos + 1)
            return False

        if quant == "?":
            # Zero occurrences
            if dfs(idx + 1, pos):
                return True
            # One occurrence
            if pos < text_len and _atom_matches(atom, text[pos]):
                return dfs(idx + 1, pos + 1)
            return False

        # quant is '*' or '+'
        min_matches = 1 if quant == "+" else 0

        if min_matches == 1:
            if pos >= text_len or not _atom_matches(atom, text[pos]):
                return False

        # Gather all possible positions after consuming matches.
        positions = [pos + min_matches]
        nxt = pos + min_matches
        while nxt < text_len and _atom_matches(atom, text[nxt]):
            nxt += 1
            positions.append(nxt)

        # Try most-greedy first, backtracking to fewer matches.
        for p in reversed(positions):
            if dfs(idx + 1, p):
                return True
        return False

    return dfs(0, 0)
