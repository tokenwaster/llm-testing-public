def match(pattern: str, text: str) -> bool:
    def parse_class(p, i):
        i += 1  # skip '['
        negate = False
        if i < len(p) and p[i] == '^':
            negate = True
            i += 1

        chars = set()
        ranges = []

        while i < len(p) and p[i] != ']':
            if i + 2 < len(p) and p[i + 1] == '-' and p[i + 2] != ']':
                lo, hi = p[i], p[i + 2]
                if lo > hi:
                    raise ValueError(f"Invalid range {lo}-{hi} in character class")
                ranges.append((lo, hi))
                i += 3
            else:
                chars.add(p[i])
                i += 1

        if i >= len(p):
            raise ValueError("Unclosed character class '['")

        i += 1  # skip ']'

        def cls_match(c, _chars=chars, _ranges=ranges, _negate=negate):
            hit = c in _chars or any(lo <= c <= hi for lo, hi in _ranges)
            return (not hit) if _negate else hit

        return cls_match, i

    def parse_elements(p):
        elements = []
        i = 0
        while i < len(p):
            ch = p[i]
            if ch in ('*', '+', '?'):
                raise ValueError(f"Quantifier '{ch}' without preceding element at index {i}")
            if ch == '[':
                matcher, i = parse_class(p, i)
            elif ch == '.':
                matcher = lambda c: True
                i += 1
            else:
                literal = ch
                matcher = lambda c, _l=literal: c == _l
                i += 1

            quantifier = None
            if i < len(p) and p[i] in ('*', '+', '?'):
                quantifier = p[i]
                i += 1
                if i < len(p) and p[i] in ('*', '+', '?'):
                    raise ValueError(f"Multiple consecutive quantifiers at index {i}")

            elements.append((matcher, quantifier))

        return elements

    def do_match(elements, ei, text, ti):
        if ei == len(elements):
            return ti == len(text)

        matcher, quantifier = elements[ei]

        if quantifier is None:
            if ti < len(text) and matcher(text[ti]):
                return do_match(elements, ei + 1, text, ti + 1)
            return False

        if quantifier == '?':
            if do_match(elements, ei + 1, text, ti):
                return True
            if ti < len(text) and matcher(text[ti]):
                return do_match(elements, ei + 1, text, ti + 1)
            return False

        if quantifier == '*':
            j = ti
            while True:
                if do_match(elements, ei + 1, text, j):
                    return True
                if j < len(text) and matcher(text[j]):
                    j += 1
                else:
                    return False

        if quantifier == '+':
            if ti >= len(text) or not matcher(text[ti]):
                return False
            j = ti + 1
            while True:
                if do_match(elements, ei + 1, text, j):
                    return True
                if j < len(text) and matcher(text[j]):
                    j += 1
                else:
                    return False

    elements = parse_elements(pattern)
    return do_match(elements, 0, text, 0)
