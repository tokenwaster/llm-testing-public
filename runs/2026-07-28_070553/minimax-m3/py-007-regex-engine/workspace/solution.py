class _PatternError(ValueError):
    pass


def _parse(pattern: str):
    """Parse pattern into a list of tokens (single characters are 'literal')."""
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == '[':
            # parse character class
            j = i + 1
            negate = False
            chars = []
            if j < n and pattern[j] == '^':
                negate = True
                j += 1
            # Track the start of the class for error checking
            # Need at least one character or range before ']'
            class_chars = []
            if j >= n:
                raise _PatternError("Unclosed character class")
            while j < n and pattern[j] != ']':
                c1 = pattern[j]
                # Handle escape? Not required by spec, but we should handle '-' properly.
                if c1 == '\\' and j + 1 < n:
                    # Allow escaping for completeness (optional)
                    raise _PatternError("Escape sequences not supported")
                if j + 1 < n and pattern[j + 1] == '-':
                    # This is a range
                    if j + 2 >= n or pattern[j + 2] == ']':
                        raise _PatternError("Unterminated range in character class")
                    c2 = pattern[j + 2]
                    if ord(c1) > ord(c2):
                        raise _PatternError("Range out of order")
                    for code in range(ord(c1), ord(c2) + 1):
                        class_chars.append(chr(code))
                    j += 3
                else:
                    class_chars.append(c1)
                    j += 1
            if j >= n:
                raise _PatternError("Unclosed character class")
            # j points at ']'
            if not class_chars:
                raise _PatternError("Empty character class")
            if negate:
                def make_neg_check(chars_set):
                    def check(ch):
                        return ch not in chars_set
                    return check
                check_fn = make_neg_check(set(class_chars))
            else:
                def make_pos_check(chars_set):
                    def check(ch):
                        return ch in chars_set
                    return check
                check_fn = make_pos_check(set(class_chars))
            tokens.append(('class', check_fn))
            i = j + 1  # skip ']'
        elif c == '\\':
            if i + 1 >= n:
                raise _PatternError("Trailing backslash")
            # Support basic escapes
            esc = pattern[i + 1]
            mapping = {
                'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                '.': '.', '*': '*', '+': '+', '?': '?',
                '[': '[', ']': ']', '^': '^', '-': '-',
            }
            if esc not in mapping:
                raise _PatternError(f"Unsupported escape: \\{esc}")
            tokens.append(('literal', mapping[esc]))
            i += 2
        elif c in '*+?':
            if not tokens:
                raise _PatternError(f"Quantifier {c!r} with nothing before it")
            prev_type, prev_val = tokens[-1]
            if prev_type == 'quantifier':
                raise _PatternError(f"Quantifier {c!r} after quantifier")
            tokens.append(('quantifier', c))
            i += 1
        elif c == '.':
            tokens.append(('dot', None))
            i += 1
        else:
            tokens.append(('literal', c))
            i += 1
    return tokens


def match(pattern: str, text: str) -> bool:
    try:
        tokens = _parse(pattern)
    except _PatternError:
        raise
    
    # Build a precompiled list of elements, each element is:
    # - ('literal', char)
    # - ('dot', None)
    # - ('class', fn)
    # - ('quantifier', kind, element) where kind in {'*','+','?'} and element is a single token
    
    elements = []
    i = 0
    while i < len(tokens):
        ttype, tval = tokens[i]
        if ttype in ('literal', 'dot', 'class'):
            if i + 1 < len(tokens) and tokens[i + 1][0] == 'quantifier':
                qkind = tokens[i + 1][1]
                elements.append(('quantifier', qkind, (ttype, tval)))
                i += 2
            else:
                elements.append((ttype, tval))
                i += 1
        else:
            # Should not reach here; quantifiers were already consumed.
            raise _PatternError("Internal parse error")
    
    # Now do recursive backtracking match.
    # State: index in elements and index in text.
    # We memoize (ei, ti) -> result (bool) to avoid exponential blowup.
    from functools import lru_cache
    
    @lru_cache(maxsize=None)
    def match_here(ei: int, ti: int) -> bool:
        # ei: index into elements; ti: index into text
        if ei == len(elements):
            return ti == len(text)
        el = elements[ei]
        if el[0] == 'quantifier':
            # quantifier applied to a single element
            kind = el[1]
            elem = el[2]  # ('literal'|'dot'|'class', val)
            e_type, e_val = elem
            if kind == '?':
                # try zero
                if match_here(ei + 1, ti):
                    return True
                # try one (if possible)
                if ti < len(text) and _match_one(elem, text[ti]):
                    return match_here(ei + 1, ti + 1)
                return False
            elif kind == '*':
                # Greedy: try matching as many as possible first via inner loop, but
                # since we want backtracking safety, we manually iterate counts.
                # Try count = 0, 1, 2, ...
                count = 0
                while True:
                    if match_here(ei + 1, ti):
                        return True
                    if ti + count < len(text) and _match_one(elem, text[ti + count]):
                        count += 1
                    else:
                        return False
            elif kind == '+':
                # Must match at least one.
                if not (ti < len(text) and _match_one(elem, text[ti])):
                    return False
                # Now handle like *, but starting from count=1
                count = 1
                # similar logic: from here, treat as * of the same element at position ti+1
                # but reusing logic: try zero or more of (same element) at position ti+count
                while True:
                    if match_here(ei + 1, ti + count):
                        return True
                    if ti + count < len(text) and _match_one(elem, text[ti + count]):
                        count += 1
                    else:
                        return False
        else:
            # single element (literal, dot, or class)
            if ti >= len(text):
                return False
            if _match_one(el, text[ti]):
                return match_here(ei + 1, ti + 1)
            return False
        return False
    
    def _match_one(elem, ch):
        if elem[0] == 'literal':
            return ch == elem[1]
        elif elem[0] == 'dot':
            return True
        elif elem[0] == 'class':
            # elem is ('class', check_fn)
            return elem[1](ch)
        return False
    
    return match_here(0, 0)
