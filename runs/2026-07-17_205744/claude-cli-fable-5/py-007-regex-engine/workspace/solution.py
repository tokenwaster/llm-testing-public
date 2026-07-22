def match(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the entire `text`.

    Supported syntax: literals, '.', '*', '+', '?', character classes
    with ranges and negation ([abc], [a-z0-9], [^abc]).
    Raises ValueError on malformed patterns.
    """
    tokens = _tokenize(pattern)
    return _match_tokens(tokens, 0, text, 0)


class _Token:
    __slots__ = ("kind", "chars", "negated", "quant")

    def __init__(self, kind, chars=None, negated=False, quant=None):
        self.kind = kind          # 'literal', 'dot', or 'class'
        self.chars = chars        # for 'literal': the char; for 'class': set of chars
        self.negated = negated    # for 'class'
        self.quant = quant        # None, '*', '+', or '?'

    def matches_char(self, ch):
        if self.kind == "dot":
            return True
        if self.kind == "literal":
            return ch == self.chars
        # class
        return (ch in self.chars) != self.negated


def _tokenize(pattern):
    tokens = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch in "*+?":
            raise ValueError(
                f"quantifier {ch!r} at position {i} has no preceding element"
            )
        if ch == "[":
            token, i = _parse_class(pattern, i)
        elif ch == ".":
            token = _Token("dot")
            i += 1
        else:
            token = _Token("literal", chars=ch)
            i += 1
        # Attach at most one quantifier to this element.
        if i < n and pattern[i] in "*+?":
            token.quant = pattern[i]
            i += 1
            if i < n and pattern[i] in "*+?":
                raise ValueError(
                    f"quantifier {pattern[i]!r} at position {i} follows a quantifier"
                )
        tokens.append(token)
    return tokens


def _parse_class(pattern, start):
    """Parse a character class beginning at pattern[start] == '['.

    Returns (token, index_after_closing_bracket).
    """
    i = start + 1
    n = len(pattern)
    negated = False
    if i < n and pattern[i] == "^":
        negated = True
        i += 1
    chars = set()
    first = True
    while True:
        if i >= n:
            raise ValueError(f"unclosed character class starting at position {start}")
        ch = pattern[i]
        if ch == "]" and not first:
            i += 1
            break
        first = False
        # Range like a-z: a '-' with a char on each side (and the right side
        # not the closing bracket).
        if i + 2 < n and pattern[i + 1] == "-" and pattern[i + 2] != "]":
            lo, hi = ch, pattern[i + 2]
            if ord(lo) > ord(hi):
                raise ValueError(
                    f"invalid range {lo}-{hi} in character class at position {i}"
                )
            for code in range(ord(lo), ord(hi) + 1):
                chars.add(chr(code))
            i += 3
        else:
            chars.add(ch)
            i += 1
    if not chars:
        raise ValueError(f"empty character class starting at position {start}")
    return _Token("class", chars=chars, negated=negated), i


def _match_tokens(tokens, ti, text, si):
    if ti == len(tokens):
        return si == len(text)
    token = tokens[ti]
    if token.quant is None:
        return (
            si < len(text)
            and token.matches_char(text[si])
            and _match_tokens(tokens, ti + 1, text, si + 1)
        )
    if token.quant == "?":
        if si < len(text) and token.matches_char(text[si]):
            if _match_tokens(tokens, ti + 1, text, si + 1):
                return True
        return _match_tokens(tokens, ti + 1, text, si)
    # '*' or '+': require at least one match for '+'.
    if token.quant == "+":
        if not (si < len(text) and token.matches_char(text[si])):
            return False
        si += 1
    # Greedy with backtracking: consume as many as possible, then back off.
    end = si
    while end < len(text) and token.matches_char(text[end]):
        end += 1
    for stop in range(end, si - 1, -1):
        if _match_tokens(tokens, ti + 1, text, stop):
            return True
    return False
