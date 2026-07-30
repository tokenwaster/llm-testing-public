from collections import namedtuple

Token = namedtuple("Token", ["kind", "value", "negated", "quant"])


def match(pattern: str, text: str) -> bool:
    tokens = _tokenize(pattern)
    return _match_tokens(tokens, text, 0, 0)


def _tokenize(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c == "[":
            i += 1
            if i >= n:
                raise ValueError("unclosed character class")

            negated = False
            if pattern[i] == "^":
                negated = True
                i += 1

            chars = set()
            while i < n and pattern[i] != "]":
                # Range like a-z or 0-9
                if (
                    i + 2 < n
                    and pattern[i + 1] == "-"
                    and pattern[i + 2] != "]"
                ):
                    lo = pattern[i]
                    hi = pattern[i + 2]
                    if lo > hi:
                        raise ValueError(
                            f"invalid character range {lo}-{hi}"
                        )
                    chars.update(chr(v) for v in range(ord(lo), ord(hi) + 1))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1

            if i >= n:
                raise ValueError("unclosed character class")
            i += 1  # skip ']'

            tokens.append(Token("class", chars, negated, None))

        elif c == ".":
            tokens.append(Token("dot", None, False, None))
            i += 1

        elif c in "*+?":
            raise ValueError(f"quantifier {c} has no preceding element")

        else:
            tokens.append(Token("literal", c, False, None))
            i += 1

        # Attach a following quantifier, if any.
        if i < n and pattern[i] in "*+?":
            tokens[-1] = tokens[-1]._replace(quant=pattern[i])
            i += 1

    return tokens


def _match_tokens(tokens, text, ti, tj):
    if ti == len(tokens):
        return tj == len(text)

    tok = tokens[ti]
    quant = tok.quant

    if quant == "?":
        if _match_one(tok, text, tj) and _match_tokens(
            tokens, text, ti + 1, tj + 1
        ):
            return True
        return _match_tokens(tokens, text, ti + 1, tj)

    if quant == "*":
        max_count = 0
        k = tj
        while k < len(text) and _match_one(tok, text, k):
            max_count += 1
            k += 1
        for count in range(max_count, -1, -1):
            if _match_tokens(tokens, text, ti + 1, tj + count):
                return True
        return False

    if quant == "+":
        if not _match_one(tok, text, tj):
            return False
        max_count = 1
        k = tj + 1
        while k < len(text) and _match_one(tok, text, k):
            max_count += 1
            k += 1
        for count in range(max_count, 0, -1):
            if _match_tokens(tokens, text, ti + 1, tj + count):
                return True
        return False

    # No quantifier: exactly one match required.
    if not _match_one(tok, text, tj):
        return False
    return _match_tokens(tokens, text, ti + 1, tj + 1)


def _match_one(tok, text, pos):
    if pos >= len(text):
        return False
    ch = text[pos]

    if tok.kind == "dot":
        return True
    if tok.kind == "literal":
        return ch == tok.value
    if tok.kind == "class":
        in_set = ch in tok.value
        return (not in_set) if tok.negated else in_set
    return False
