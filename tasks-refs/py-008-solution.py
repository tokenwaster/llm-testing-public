"""Reference: recursive-descent JSON parser (v0.5 py-008)."""


class _Fail(Exception):
    pass


def parse(text: str):
    try:
        val, i = _value(text, _ws(text, 0))
        if _ws(text, i) != len(text):
            raise _Fail("trailing garbage")
        return val
    except (_Fail, IndexError):
        return None


def _ws(s, i):
    while i < len(s) and s[i] in " \t\n\r":
        i += 1
    return i


def _value(s, i):
    if i >= len(s):
        raise _Fail("eof")
    c = s[i]
    if c == "{":
        return _obj(s, i)
    if c == "[":
        return _arr(s, i)
    if c == '"':
        return _str(s, i)
    if c == "t":
        if s[i:i + 4] == "true":
            return True, i + 4
        raise _Fail()
    if c == "f":
        if s[i:i + 5] == "false":
            return False, i + 5
        raise _Fail()
    if c == "n":
        if s[i:i + 4] == "null":
            return None, i + 4
        raise _Fail()
    return _num(s, i)


def _obj(s, i):
    i = _ws(s, i + 1)
    out = {}
    if i < len(s) and s[i] == "}":
        return out, i + 1
    while True:
        i = _ws(s, i)
        if i >= len(s) or s[i] != '"':
            raise _Fail("key")
        key, i = _str(s, i)
        i = _ws(s, i)
        if i >= len(s) or s[i] != ":":
            raise _Fail("colon")
        val, i = _value(s, _ws(s, i + 1))
        out[key] = val
        i = _ws(s, i)
        if i >= len(s):
            raise _Fail()
        if s[i] == ",":
            i += 1
            continue
        if s[i] == "}":
            return out, i + 1
        raise _Fail()


def _arr(s, i):
    i = _ws(s, i + 1)
    out = []
    if i < len(s) and s[i] == "]":
        return out, i + 1
    while True:
        val, i = _value(s, _ws(s, i))
        out.append(val)
        i = _ws(s, i)
        if i >= len(s):
            raise _Fail()
        if s[i] == ",":
            i += 1
            continue
        if s[i] == "]":
            return out, i + 1
        raise _Fail()


_ESC = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
        "n": "\n", "r": "\r", "t": "\t"}


def _str(s, i):
    i += 1
    out = []
    while True:
        if i >= len(s):
            raise _Fail("unterminated")
        c = s[i]
        if c == '"':
            return "".join(out), i + 1
        if c == "\\":
            e = s[i + 1] if i + 1 < len(s) else ""
            if e in _ESC:
                out.append(_ESC[e])
                i += 2
            elif e == "u":
                hex4 = s[i + 2:i + 6]
                if len(hex4) != 4 or any(h not in "0123456789abcdefABCDEF"
                                         for h in hex4):
                    raise _Fail("bad \\u")
                out.append(chr(int(hex4, 16)))
                i += 6
            else:
                raise _Fail("bad escape")
        else:
            out.append(c)
            i += 1


def _num(s, i):
    j = i
    if j < len(s) and s[j] == "-":
        j += 1
    if j >= len(s) or not s[j].isdigit():
        raise _Fail("number")
    if s[j] == "0" and j + 1 < len(s) and s[j + 1].isdigit():
        raise _Fail("leading zero")
    while j < len(s) and s[j].isdigit():
        j += 1
    is_float = False
    if j < len(s) and s[j] == ".":
        is_float = True
        j += 1
        if j >= len(s) or not s[j].isdigit():
            raise _Fail("bad fraction")
        while j < len(s) and s[j].isdigit():
            j += 1
    if j < len(s) and s[j] in "eE":
        is_float = True
        j += 1
        if j < len(s) and s[j] in "+-":
            j += 1
        if j >= len(s) or not s[j].isdigit():
            raise _Fail("bad exponent")
        while j < len(s) and s[j].isdigit():
            j += 1
    raw = s[i:j]
    return (float(raw) if is_float else int(raw)), j
