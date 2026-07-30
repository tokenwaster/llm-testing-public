import sys


class _Literal:
    __slots__ = ('ch',)
    def __init__(self, ch):
        self.ch = ch
    def matches(self, ch):
        return ch == self.ch


class _Any:
    __slots__ = ()
    def matches(self, ch):
        return True


class _CharClass:
    __slots__ = ('negated', 'ranges', 'chars')
    def __init__(self, negated, ranges, chars):
        self.negated = negated
        self.ranges = ranges
        self.chars = chars
    def matches(self, ch):
        in_class = ch in self.chars
        if not in_class:
            o = ord(ch)
            for s, e in self.ranges:
                if s <= o <= e:
                    in_class = True
                    break
        return in_class != self.negated


def match(pattern: str, text: str) -> bool:
    nodes = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            i += 1
            negated = False
            if i < n and pattern[i] == '^':
                negated = True
                i += 1
            ranges = []
            chars = set()
            closed = False
            while i < n:
                if pattern[i] == ']':
                    closed = True
                    i += 1
                    break
                if (i + 1 < n and pattern[i + 1] == '-'
                        and i + 2 < n and pattern[i + 2] != ']'):
                    start = pattern[i]
                    end = pattern[i + 2]
                    s = ord(start)
                    e = ord(end)
                    if s > e:
                        s, e = e, s
                    ranges.append((s, e))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            if not closed:
                raise ValueError("unclosed character class")
            atom = _CharClass(negated, ranges, chars)
            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            else:
                quant = ''
            nodes.append((atom, quant))
        elif c in '*+?':
            raise ValueError("quantifier with nothing to repeat")
        else:
            atom = _Any() if c == '.' else _Literal(c)
            i += 1
            if i < n and pattern[i] in '*+?':
                quant = pattern[i]
                i += 1
            else:
                quant = ''
            nodes.append((atom, quant))

    sys.setrecursionlimit(max(10000, len(text) + len(pattern) + 1000))
    N = len(nodes)
    L = len(text)

    def match_nodes(idx, pos):
        if idx == N:
            return pos == L
        atom, quant = nodes[idx]
        if quant == '':
            if pos < L and atom.matches(text[pos]):
                return match_nodes(idx + 1, pos + 1)
            return False
        elif quant == '?':
            if match_nodes(idx + 1, pos):
                return True
            if pos < L and atom.matches(text[pos]):
                return match_nodes(idx + 1, pos + 1)
            return False
        elif quant == '*':
            return match_star(atom, idx + 1, pos)
        elif quant == '+':
            if pos >= L or not atom.matches(text[pos]):
                return False
            return match_star(atom, idx + 1, pos + 1)
        return False

    def match_star(atom, next_idx, pos):
        if match_nodes(next_idx, pos):
            return True
        if pos < L and atom.matches(text[pos]):
            return match_star(atom, next_idx, pos + 1)
        return False

    return match_nodes(0, 0)
