class _CharClass:
    __slots__ = ('chars', 'ranges', 'negate')

    def __init__(self, chars, ranges, negate):
        self.chars = chars
        self.ranges = ranges
        self.negate = negate

    def matches(self, c):
        if c in self.chars:
            return not self.negate
        for lo, hi in self.ranges:
            if lo <= c <= hi:
                return not self.negate
        return self.negate


class _Atom:
    __slots__ = ('kind', 'value', 'char_class', 'quantifier')

    def __init__(self, kind, value=None, char_class=None, quantifier=None):
        self.kind = kind
        self.value = value
        self.char_class = char_class
        self.quantifier = quantifier


def _parse(pattern):
    atoms = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            j = i + 1
            negate = False
            if j < n and pattern[j] == '^':
                negate = True
                j += 1
            chars = set()
            ranges = []
            while j < n and pattern[j] != ']':
                # A range is triggered only when '-' is between two
                # non-']' characters within the class.
                if (j + 2 < n
                        and pattern[j + 1] == '-'
                        and pattern[j + 2] != ']'):
                    lo = pattern[j]
                    hi = pattern[j + 2]
                    ranges.append((lo, hi))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= n:
                raise ValueError("Unclosed character class")
            atom = _Atom('class',
                         char_class=_CharClass(chars, ranges, negate))
            i = j + 1
        elif c in '*+?':
            raise ValueError(
                f"Quantifier '{c}' with nothing before it")
        else:
            if c == '.':
                atom = _Atom('dot')
            else:
                atom = _Atom('literal', value=c)
            i += 1

        # Optional quantifier on the atom we just built.
        if i < n and pattern[i] in '*+?':
            atom.quantifier = pattern[i]
            i += 1

        atoms.append(atom)
    return atoms


def _atom_matches(atom, c):
    if atom.kind == 'literal':
        return c == atom.value
    if atom.kind == 'dot':
        return True
    if atom.kind == 'class':
        return atom.char_class.matches(c)
    return False


def _match_atoms(atoms, pos, text, ti, tn):
    if pos == len(atoms):
        return ti == tn

    atom = atoms[pos]
    q = atom.quantifier

    if q is None:
        if ti < tn and _atom_matches(atom, text[ti]):
            return _match_atoms(atoms, pos + 1, text, ti + 1, tn)
        return False

    if q == '?':
        if ti < tn and _atom_matches(atom, text[ti]):
            if _match_atoms(atoms, pos + 1, text, ti + 1, tn):
                return True
        return _match_atoms(atoms, pos + 1, text, ti, tn)

    if q == '*':
        # Greedy: count the maximum number of matches, then backtrack.
        max_count = 0
        while (ti + max_count < tn
               and _atom_matches(atom, text[ti + max_count])):
            max_count += 1
        for n in range(max_count, -1, -1):
            if _match_atoms(atoms, pos + 1, text, ti + n, tn):
                return True
        return False

    if q == '+':
        # Must consume at least one character.
        if ti >= tn or not _atom_matches(atom, text[ti]):
            return False
        max_count = 1
        while (ti + max_count < tn
               and _atom_matches(atom, text[ti + max_count])):
            max_count += 1
        for n in range(max_count, 0, -1):
            if _match_atoms(atoms, pos + 1, text, ti + n, tn):
                return True
        return False

    return False  # Unreachable for well-formed patterns.


def match(pattern: str, text: str) -> bool:
    atoms = _parse(pattern)
    return _match_atoms(atoms, 0, text, 0, len(text))
