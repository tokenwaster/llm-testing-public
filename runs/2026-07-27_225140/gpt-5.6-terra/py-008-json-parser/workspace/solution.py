class _JSONParseError(Exception):
    pass


def parse(text: str):
    if not isinstance(text, str):
        return None

    length = len(text)
    index = 0

    def skip_whitespace():
        nonlocal index
        while index < length and text[index] in " \t\r\n":
            index += 1

    def parse_string():
        nonlocal index

        if index >= length or text[index] != '"':
            raise _JSONParseError

        index += 1
        result = []

        while index < length:
            ch = text[index]
            index += 1

            if ch == '"':
                return "".join(result)

            if ord(ch) < 0x20:
                raise _JSONParseError

            if ch != "\\":
                result.append(ch)
                continue

            if index >= length:
                raise _JSONParseError

            escape = text[index]
            index += 1

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

            if escape in escapes:
                result.append(escapes[escape])
                continue

            if escape != "u" or index + 4 > length:
                raise _JSONParseError

            hex_digits = text[index:index + 4]
            if any(c not in "0123456789abcdefABCDEF" for c in hex_digits):
                raise _JSONParseError

            codepoint = int(hex_digits, 16)
            index += 4

            # Combine UTF-16 surrogate pairs when present.
            if 0xD800 <= codepoint <= 0xDBFF:
                if (
                    index + 6 <= length
                    and text[index] == "\\"
                    and text[index + 1] == "u"
                ):
                    low_hex = text[index + 2:index + 6]
                    if all(c in "0123456789abcdefABCDEF" for c in low_hex):
                        low = int(low_hex, 16)
                        if 0xDC00 <= low <= 0xDFFF:
                            codepoint = (
                                0x10000
                                + ((codepoint - 0xD800) << 10)
                                + (low - 0xDC00)
                            )
                            index += 6

            result.append(chr(codepoint))

        raise _JSONParseError

    def parse_number():
        nonlocal index

        start = index

        if index < length and text[index] == "-":
            index += 1

        if index >= length:
            raise _JSONParseError

        if text[index] == "0":
            index += 1
            if index < length and text[index].isdigit():
                raise _JSONParseError
        elif "1" <= text[index] <= "9":
            index += 1
            while index < length and text[index].isdigit():
                index += 1
        else:
            raise _JSONParseError

        is_float = False

        if index < length and text[index] == ".":
            is_float = True
            index += 1
            if index >= length or not text[index].isdigit():
                raise _JSONParseError
            while index < length and text[index].isdigit():
                index += 1

        if index < length and text[index] in "eE":
            is_float = True
            index += 1
            if index < length and text[index] in "+-":
                index += 1
            if index >= length or not text[index].isdigit():
                raise _JSONParseError
            while index < length and text[index].isdigit():
                index += 1

        number_text = text[start:index]
        return float(number_text) if is_float else int(number_text)

    def parse_array():
        nonlocal index

        index += 1
        skip_whitespace()

        result = []
        if index < length and text[index] == "]":
            index += 1
            return result

        while True:
            skip_whitespace()
            result.append(parse_value())
            skip_whitespace()

            if index >= length:
                raise _JSONParseError

            if text[index] == "]":
                index += 1
                return result

            if text[index] != ",":
                raise _JSONParseError

            index += 1
            skip_whitespace()

            if index >= length or text[index] == "]":
                raise _JSONParseError

    def parse_object():
        nonlocal index

        index += 1
        skip_whitespace()

        result = {}
        if index < length and text[index] == "}":
            index += 1
            return result

        while True:
            skip_whitespace()

            if index >= length or text[index] != '"':
                raise _JSONParseError

            key = parse_string()
            skip_whitespace()

            if index >= length or text[index] != ":":
                raise _JSONParseError

            index += 1
            skip_whitespace()
            result[key] = parse_value()
            skip_whitespace()

            if index >= length:
                raise _JSONParseError

            if text[index] == "}":
                index += 1
                return result

            if text[index] != ",":
                raise _JSONParseError

            index += 1
            skip_whitespace()

            if index >= length or text[index] == "}":
                raise _JSONParseError

    def parse_value():
        nonlocal index

        skip_whitespace()

        if index >= length:
            raise _JSONParseError

        ch = text[index]

        if ch == '"':
            return parse_string()

        if ch == "{":
            return parse_object()

        if ch == "[":
            return parse_array()

        if ch == "-" or ch.isdigit():
            return parse_number()

        if text.startswith("true", index):
            index += 4
            return True

        if text.startswith("false", index):
            index += 5
            return False

        if text.startswith("null", index):
            index += 4
            return None

        raise _JSONParseError

    try:
        skip_whitespace()
        value = parse_value()
        skip_whitespace()

        if index != length:
            return None

        return value
    except (_JSONParseError, RecursionError, ValueError, OverflowError):
        return None
