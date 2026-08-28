"""
solution.py

A small regex engine supporting full-string matching with:
  - literal characters
  - '.'   any single character
  - '*'   zero or more of the preceding element
  - '+'   one or more of the preceding element
  - '?'   zero or one of the preceding element
  - character classes [abc], ranges [a-z0-9], negation [^abc]

No regex libraries are used; the pattern is parsed by hand and matched
with recursive backtracking (with memoization of failed states).
"""

from functools import lru_cache


def match(pattern: str, text: str) -> bool:
    """Return True iff `pattern` matches the ENTIRE `text`.

    Raises ValueError for malformed patterns, e.g. an unclosed '[',
    an invalid character range, or a quantifier ('*', '+', '?') with
    nothing before it to repeat.
    """
    n = len(pattern)

    # ------------------------------ parsing ------------------------------
    # Each entry: (atom, quantifier) where atom is one of
    #   ('char', c) | ('dot',) | ('class', members_set, negated_bool)
    # and quantifier is None, '*', '+' or '?'.
    atoms = []
    i = 0
    while i < n:
        c = pattern[i]

        if c == '[':
            j = i + 1
            negated = False
            if j < n and pattern[j] == '^':
                negated = True
                j += 1
            members = set()
            closed = False
            while j < n:
                if pattern[j] == ']':
                    closed = True
                    j += 1
                    break
                # Possible range x-y (y must exist and not be the closing ']')
                if (j + 2 < n and pattern[j + 1] == '-'
                        and pattern[j + 2] != ']'):
                    lo, hi = pattern[j], pattern[j + 2]
                    if ord(lo) > ord(hi):
                        raise ValueError(
                            "invalid character range '%s-%s' in pattern "
                            "at position %d" % (lo, hi, i))
                    for o in range(ord(lo), ord(hi) + 1):
                        members.add(chr(o))
                    j += 3
                else:
                    members.add(pattern[j])
                    j += 1
            if not closed:
                raise ValueError(
                    "unterminated character class in pattern at position %d"
                    % i)
            atom = ('class', members, negated)
            i = j
        elif c == '.':
            atom = ('dot',)
            i += 1
        elif c in '*+?':
            raise ValueError(
                "quantifier '%s' at position %d has nothing to repeat"
                % (c, i))
        else:
            atom = ('char', c)
            i += 1

        # A single trailing quantifier may apply to any atom.
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in '*+?':
                raise ValueError(
                    "multiple quantifiers at position %d in pattern" % (i - 1))

        atoms.append((atom, quant))

    # ------------------------------ matching -----------------------------
    m = len(text)

    def char_matches(atom, ch):
        kind = atom[0]
        if kind == 'dot':
            return True
        if kind == 'char':
            return ch == atom[1]
        _, members, negated = atom
        return (ch in members) != negated

    @lru_cache(maxsize=None)
    def match_from(ai, ti):
        """Can atoms[ai:] match text[ti:] entirely?"""
        if ai == len(atoms):
            return ti == m

        atom, quant = atoms[ai]

        if quant is None:
            return (ti < m and char_matches(atom, text[ti])
                    and match_from(ai + 1, ti + 1))

        if quant == '?':
            if match_from(ai + 1, ti):          # zero occurrences
                return True
            return (ti < m and char_matches(atom, text[ti])
                    and match_from(ai + 1, ti + 1))  # one occurrence

        if quant == '*':
            if match_from(ai + 1, ti):          # zero occurrences
                return True
            k = ti
            while k < m and char_matches(atom, text[k]):
                k += 1
                if match_from(ai + 1, k):       # 1..k occurrences
                    return True
            return False

        # quant == '+'
        k = ti
        while k < m and char_matches(atom, text[k]):
            k += 1                              # at least one occurrence
            if match_from(ai + 1, k):
                return True
        return False

    return match_from(0, 0)
