def parse(text: str):
    if not isinstance(text, str):
        return None

    n = len(text)
    i = 0
    whitespace = " \t\r\n"
    hex_digits = "0123456789abcdefABCDEF"
    escapes = {
        '"': '"',
        "\\": "\\",
        "/": "/",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
    }

    class InvalidJSON(Exception):
        pass

    def skip_whitespace():
        nonlocal i
        while i < n and text[i] in whitespace:
            i += 1

    def read_hex():
        nonlocal i
        digits = text[i:i + 4]
        if len(digits) != 4 or any(c not in hex_digits for c in digits):
            raise InvalidJSON
        i += 4
        return int(digits, 16)

    def read_string():
        nonlocal i
        i += 1
        result = []

        while i < n:
            c = text[i]
            i += 1
            if c == '"':
                return "".join(result)
            if ord(c) < 0x20:
                raise InvalidJSON
            if c != "\\":
                result.append(c)
                continue

            if i >= n:
                raise InvalidJSON
            escape = text[i]
            i += 1

            if escape in escapes:
                result.append(escapes[escape])
            elif escape == "u":
                code = read_hex()
                if 0xD800 <= code <= 0xDBFF and text[i:i + 2] == "\\u":
                    saved = i
                    i += 2
                    low = read_hex()
                    if 0xDC00 <= low <= 0xDFFF:
                        code = 0x10000 + ((code - 0xD800) << 10) + low - 0xDC00
                    else:
                        i = saved
                result.append(chr(code))
            else:
                raise InvalidJSON

        raise InvalidJSON

    def read_number():
        nonlocal i
        start = i

        if text[i] == "-":
            i += 1
        if i >= n:
            raise InvalidJSON

        if text[i] == "0":
            i += 1
        elif "1" <= text[i] <= "9":
            while i < n and "0" <= text[i] <= "9":
                i += 1
        else:
            raise InvalidJSON

        is_float = False
        if i < n and text[i] == ".":
            is_float = True
            i += 1
            fraction_start = i
            while i < n and "0" <= text[i] <= "9":
                i += 1
            if i == fraction_start:
                raise InvalidJSON

        if i < n and text[i] in "eE":
            is_float = True
            i += 1
            if i < n and text[i] in "+-":
                i += 1
            exponent_start = i
            while i < n and "0" <= text[i] <= "9":
                i += 1
            if i == exponent_start:
                raise InvalidJSON

        token = text[start:i]
        if is_float:
            return float(token)

        negative = token[0] == "-"
        value = 0
        for digit in token[1:] if negative else token:
            value = value * 10 + ord(digit) - ord("0")
        return -value if negative else value

    def read_value():
        nonlocal i
        skip_whitespace()
        if i >= n:
            raise InvalidJSON

        c = text[i]
        if c == '"':
            return read_string()

        if c == "[":
            i += 1
            result = []
            skip_whitespace()
            if i < n and text[i] == "]":
                i += 1
                return result
            while True:
                result.append(read_value())
                skip_whitespace()
                if i >= n:
                    raise InvalidJSON
                delimiter = text[i]
                i += 1
                if delimiter == "]":
                    return result
                if delimiter != ",":
                    raise InvalidJSON

        if c == "{":
            i += 1
            result = {}
            skip_whitespace()
            if i < n and text[i] == "}":
                i += 1
                return result
            while True:
                skip_whitespace()
                if i >= n or text[i] != '"':
                    raise InvalidJSON
                key = read_string()
                skip_whitespace()
                if i >= n or text[i] != ":":
                    raise InvalidJSON
                i += 1
                result[key] = read_value()
                skip_whitespace()
                if i >= n:
                    raise InvalidJSON
                delimiter = text[i]
                i += 1
                if delimiter == "}":
                    return result
                if delimiter != ",":
                    raise InvalidJSON

        for literal, value in (("true", True), ("false", False), ("null", None)):
            if text.startswith(literal, i):
                i += len(literal)
                return value

        if c == "-" or "0" <= c <= "9":
            return read_number()

        raise InvalidJSON

    try:
        result = read_value()
        skip_whitespace()
        if i != n:
            return None
        return result
    except (InvalidJSON, ValueError, OverflowError, RecursionError):
        return None
