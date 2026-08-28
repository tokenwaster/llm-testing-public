"""solution.py — A strict JSON parser written from scratch (no `json` module).

Implements the full RFC 8259 grammar via an explicit-state, iterative
recursive-descent style parser, so arbitrarily deep nesting cannot overflow
the call stack.  Any malformed input yields None.
"""

__all__ = ["parse"]

_WHITESPACE = " \t
\r"
_DIGITS = "0123456789"

_ESCAPES = {
    '"': '"',
    "\": "\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "
",
    "r": "\r",
    "t": "\t",
}

_HEX = {}
for _i, _ch in enumerate("0123456789abcdef"):
    _HEX[_ch] = _i
    _HEX[_ch.upper()] = _i

# Driver states.
(_VALUE, _ARR_FIRST, _ARR_AFTER, _OBJ_FIRST, _OBJ_KEY, _OBJ_COLON, _OBJ_AFTER) = range(7)


def parse(text: str):
    """Parse a JSON document and return the equivalent Python object.

    Returns None if the input is not valid JSON.  (Valid JSON ``null`` also
    maps to Python None; that ambiguity is accepted by the specification.)
    """
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    class _Invalid(Exception):
        pass

    def fail():
        raise _Invalid

    def skip_ws():
        nonlocal pos
        while pos < n and text[pos] in _WHITESPACE:
            pos += 1

    def decode_hex4():
        nonlocal pos
        if pos + 4 > n:
            fail()
        code = 0
        for k in range(pos, pos + 4):
            digit = _HEX.get(text[k])
            if digit is None:
                fail()
            code = (code << 4) | digit
        pos += 4
        return code

    def parse_string():
        nonlocal pos
        # Caller guarantees text[pos] == '"'.
        pos += 1
        parts = []
        while True:
            if pos >= n:
                fail()  # unterminated string
            ch = text[pos]
            if ch == '"':
                pos += 1
                return "".join(parts)
            if ch == "\":
                pos += 1
                if pos >= n:
                    fail()
                esc = text[pos]
                simple = _ESCAPES.get(esc)
                if simple is not None:
                    parts.append(simple)
                    pos += 1
                    continue
                if esc == "u":
                    pos += 1
                    code = decode_hex4()
                    # Combine UTF-16 surrogate pairs when present.
                    if (
                        0xD800 <= code <= 0xDBFF
                        and pos + 1 < n
                        and text[pos] == "\"
                        and text[pos + 1] == "u"
                    ):
                        resume = pos
                        pos += 2
                        low = decode_hex4()
                        if 0xDC00 <= low <= 0xDFFF:
                            code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                        else:
                            pos = resume  # not a pair; keep both escapes
                    parts.append(chr(code))
                    continue
                fail()  # unknown escape sequence
            if ch < " ":
                fail()  # raw control character inside a string
            parts.append(ch)
            pos += 1

    def parse_number():
        nonlocal pos
        start = pos
        is_float = False

        if text[pos] == "-":
            pos += 1

        # Integer part: a leading '0' must stand alone (no leading zeros).
        if pos >= n or text[pos] not in _DIGITS:
            fail()
        if text[pos] == "0":
            pos += 1
        else:
            while pos < n and text[pos] in _DIGITS:
                pos += 1

        # Fractional part.
        if pos < n and text[pos] == ".":
            is_float = True
            pos += 1
            if pos >= n or text[pos] not in _DIGITS:
                fail()
            while pos < n and text[pos] in _DIGITS:
                pos += 1

        # Exponent part.
        if pos < n and text[pos] in "eE":
            is_float = True
            pos += 1
            if pos < n and text[pos] in "+-":
                pos += 1
            if pos >= n or text[pos] not in _DIGITS:
                fail()
            while pos < n and text[pos] in _DIGITS:
                pos += 1

        literal = text[start:pos]

        # A number must be followed by a delimiter, never more digits/letters.
        if pos < n and (text[pos] in _DIGITS or text[pos].isalpha() or text[pos] in "._"):
            fail()

        try:
            return float(literal) if is_float else int(literal)
        except (ValueError, OverflowError):
            fail()

    def parse_keyword(word, value):
        nonlocal pos
        if text.startswith(word, pos):
            pos += len(word)
            return value
        fail()

    # ------------------------- iterative driver -------------------------
    try:
        state = _VALUE
        stack = []  # frames: [container, pending_key (None for arrays)]
        value = None

        while True:
            if state == _VALUE:
                skip_ws()
                if pos >= n:
                    return None
                ch = text[pos]
                if ch == '"':
                    value = parse_string()
                elif ch == "t":
                    value = parse_keyword("true", True)
                elif ch == "f":
                    value = parse_keyword("false", False)
                elif ch == "n":
                    value = parse_keyword("null", None)
                elif ch == "-" or ch in _DIGITS:
                    value = parse_number()
                elif ch == "[":
                    pos += 1
                    stack.append([[], None])
                    state = _ARR_FIRST
                    continue
                elif ch == "{":
                    pos += 1
                    stack.append([{}, None])
                    state = _OBJ_FIRST
                    continue
                else:
                    return None
            elif state == _ARR_FIRST:
                skip_ws()
                if pos >= n:
                    return None
                if text[pos] == "]":
                    pos += 1
                    value = stack.pop()[0]
                else:
                    state = _VALUE
                    continue
            elif state == _ARR_AFTER:
                skip_ws()
                if pos >= n:
                    return None
                ch = text[pos]
                if ch == ",":
                    pos += 1
                    state = _VALUE
                    continue
                if ch == "]":
                    pos += 1
                    value = stack.pop()[0]
                else:
                    return None
            elif state == _OBJ_FIRST:
                skip_ws()
                if pos >= n:
                    return None
                if text[pos] == "}":
                    pos += 1
                    value = stack.pop()[0]
                else:
                    state = _OBJ_KEY
                    continue
            elif state == _OBJ_KEY:
                skip_ws()
                if pos >= n or text[pos] != '"':
                    return None
                stack[-1][1] = parse_string()
                state = _OBJ_COLON
                continue
            elif state == _OBJ_COLON:
                skip_ws()
                if pos >= n or text[pos] != ":":
                    return None
                pos += 1
                state = _VALUE
                continue
            elif state == _OBJ_AFTER:
                skip_ws()
                if pos >= n:
                    return None
                ch = text[pos]
                if ch == ",":
                    pos += 1
                    state = _OBJ_KEY
                    continue
                if ch == "}":
                    pos += 1
                    value = stack.pop()[0]
                else:
                    return None
            else:  # defensive; unreachable
                return None

            # A finished value (scalar or freshly closed container) is in
            # `value`: attach it to its parent container, or end the document.
            if not stack:
                skip_ws()
                if pos != n:
                    return None  # trailing garbage after the document
                return value
            frame = stack[-1]
            container = frame[0]
            if isinstance(container, list):
                container.append(value)
                state = _ARR_AFTER
            else:
                key = frame[1]
                if key is None:  # defensive; unreachable
                    return None
                container[key] = value
                frame[1] = None
                state = _OBJ_AFTER
    except _Invalid:
        return None
