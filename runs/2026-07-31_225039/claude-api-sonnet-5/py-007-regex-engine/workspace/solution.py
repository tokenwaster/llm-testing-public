class Atom:
    """Represents a single pattern atom: a literal char, '.', or a char class."""
    __slots__ = ("kind", "data")

    def __init__(self, kind, data):
        # kind: 'char', 'any', or 'class'
        # data: for 'char' -> the character
        #       for 'any'  -> None
        #       for 'class'-> (set_of_chars, negate_bool)
        self.kind = kind
        self.data = data

    def matches(self, c):
        if self.kind == "char":
            return c == self.data
        elif self.kind == "any":
            return True
        elif self.kind == "class":
            chars, negate = self.data
            in_set = c in chars
            return (not in_set) if negate else in_set
        return False


def _parse_pattern(pattern):
    """Parse the pattern string into a list of (Atom, quantifier) pairs.

    quantifier is one of '*', '+', '?', or None (meaning exactly one).
    Raises ValueError on malformed patterns.
    """
    atoms = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c in "*+?":
            raise ValueError(f"Quantifier {c!r} with nothing to repeat")

        if c == "[":
            j = i + 1
            if j >= n:
                raise ValueError("Unterminated character class")

            negate = False
            if pattern[j] == "^":
                negate = True
                j += 1

            chars = set()

            # A ']' right after '[' or '[^' is treated as a literal ']'
            if j < n and pattern[j] == "]":
                chars.add("]")
                j += 1

            while j < n and pattern[j] != "]":
                # Check for a range like a-z
                if (
                    j + 2 < n
                    and pattern[j + 1] == "-"
                    and pattern[j + 2] != "]"
                ):
                    start = pattern[j]
                    end = pattern[j + 2]
                    if ord(start) > ord(end):
                        raise ValueError("Invalid character range in class")
                    for code in range(ord(start), ord(end) + 1):
                        chars.add(chr(code))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1

            if j >= n or pattern[j] != "]":
                raise ValueError("Unterminated character class")

            atom = Atom("class", (chars, negate))
            i = j + 1

        elif c == ".":
            atom = Atom("any", None)
            i += 1

        else:
            atom = Atom("char", c)
            i += 1

        quant = None
        if i < n and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1

        atoms.append((atom, quant))

    return atoms


def _match_here(atoms, ai, text, ti):
    if ai == len(atoms):
        return ti == len(text)

    atom, quant = atoms[ai]
    n = len(text)

    if quant == "*":
        i = ti
        while i < n and atom.matches(text[i]):
            i += 1
        while i >= ti:
            if _match_here(atoms, ai + 1, text, i):
                return True
            i -= 1
        return False

    elif quant == "+":
        if ti < n and atom.matches(text[ti]):
            i = ti + 1
            while i < n and atom.matches(text[i]):
                i += 1
            while i > ti:
                if _match_here(atoms, ai + 1, text, i):
                    return True
                i -= 1
            return False
        return False

    elif quant == "?":
        if ti < n and atom.matches(text[ti]):
            if _match_here(atoms, ai + 1, text, ti + 1):
                return True
        return _match_here(atoms, ai + 1, text, ti)

    else:
        if ti < n and atom.matches(text[ti]):
            return _match_here(atoms, ai + 1, text, ti + 1)
        return False


def match(pattern: str, text: str) -> bool:
    atoms = _parse_pattern(pattern)
    return _match_here(atoms, 0, text, 0)
