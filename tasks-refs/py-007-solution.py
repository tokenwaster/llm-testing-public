"""Reference: recursive backtracking regex engine (v0.5 py-007)."""


def _parse(pattern: str) -> list:
    """-> list of (matcher_desc, quantifier). matcher_desc: ('char', c) |
    ('dot',) | ('class', set, negated)."""
    elems = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c in "*+?":
            raise ValueError(f"quantifier '{c}' with nothing to repeat")
        if c == "[":
            j = i + 1
            neg = j < len(pattern) and pattern[j] == "^"
            if neg:
                j += 1
            chars = set()
            if j >= len(pattern):
                raise ValueError("unclosed class")
            while j < len(pattern) and pattern[j] != "]":
                if (j + 2 < len(pattern) and pattern[j + 1] == "-"
                        and pattern[j + 2] != "]"):
                    for o in range(ord(pattern[j]), ord(pattern[j + 2]) + 1):
                        chars.add(chr(o))
                    j += 3
                else:
                    chars.add(pattern[j])
                    j += 1
            if j >= len(pattern):
                raise ValueError("unclosed class")
            elem = ("class", chars, neg)
            i = j + 1
        elif c == ".":
            elem = ("dot",)
            i += 1
        else:
            elem = ("char", c)
            i += 1
        quant = ""
        if i < len(pattern) and pattern[i] in "*+?":
            quant = pattern[i]
            i += 1
        elems.append((elem, quant))
    return elems


def _hits(elem, ch) -> bool:
    if elem[0] == "dot":
        return True
    if elem[0] == "char":
        return ch == elem[1]
    _, chars, neg = elem
    return (ch not in chars) if neg else (ch in chars)


def match(pattern: str, text: str) -> bool:
    elems = _parse(pattern)

    def m(ei: int, ti: int) -> bool:
        if ei == len(elems):
            return ti == len(text)
        elem, quant = elems[ei]
        if quant == "":
            return (ti < len(text) and _hits(elem, text[ti])
                    and m(ei + 1, ti + 1))
        if quant == "?":
            if ti < len(text) and _hits(elem, text[ti]) and m(ei + 1, ti + 1):
                return True
            return m(ei + 1, ti)
        if quant == "+":
            if not (ti < len(text) and _hits(elem, text[ti])):
                return False
            ti += 1
        n = ti
        while n < len(text) and _hits(elem, text[n]):
            n += 1
        while n >= ti:
            if m(ei + 1, n):
                return True
            n -= 1
        return False

    return m(0, 0)
