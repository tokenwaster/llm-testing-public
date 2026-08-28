class _ParseError(Exception):
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
            raise _ParseError
        index += 1
        result = []

        while index < length:
            char = text[index]
            index += 1

            if char == '"':
                return "".join(result)

            if ord(char) < 0x20:
                raise _ParseError

            if char != "\\":
                result.append(char)
                continue

            if index >= length:
                raise _ParseError

            escape = text[index]
            index += 1
            simple_escapes = {
                '"': '"',
                "\\": "\\",
                "/": "/",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
            }

            if escape in simple_escapes:
                result.append(simple_escapes[escape])
                continue

            if escape != "u" or index + 4 > length:
                raise _ParseError

            digits = text[index:index + 4]
            if any(c not in "0123456789abcdefABCDEF" for c in digits):
                raise _ParseError
            index += 4
            codepoint = int(digits, 16)

            if 0xD800 <= codepoint <= 0xDBFF:
                if index + 6 <= length and text[index:index + 2] == "\\u":
                    low_digits = text[index + 2:index + 6]
                    if all(c in "0123456789abcdefABCDEF" for c in low_digits):
                        low = int(low_digits, 16)
                        if 0xDC00 <= low <= 0xDFFF:
                            index += 6
                            codepoint = (
                                0x10000
                                + ((codepoint - 0xD800) << 10)
                                + (low - 0xDC00)
                            )

            result.append(chr(codepoint))

        raise _ParseError

    def parse_number():
        nonlocal index
        start = index

        if index < length and text[index] == "-":
            index += 1

        if index >= length:
            raise _ParseError

        if text[index] == "0":
            index += 1
            if index < length and text[index].isdigit():
                raise _ParseError
        elif "1" <= text[index] <= "9":
            while index < length and text[index].isdigit():
                index += 1
        else:
            raise _ParseError

        is_float = False

        if index < length and text[index] == ".":
            is_float = True
            index += 1
            if index >= length or not text[index].isdigit():
                raise _ParseError
            while index < length and text[index].isdigit():
                index += 1

        if index < length and text[index] in "eE":
            is_float = True
            index += 1
            if index < length and text[index] in "+-":
                index += 1
            if index >= length or not text[index].isdigit():
                raise _ParseError
            while index < length and text[index].isdigit():
                index += 1

        number = text[start:index]
        try:
            return float(number) if is_float else int(number)
        except (ValueError, OverflowError):
            raise _ParseError

    def parse_array():
        nonlocal index
        index += 1
        result = []
        skip_whitespace()

        if index < length and text[index] == "]":
            index += 1
            return result

        while True:
            result.append(parse_value())
            skip_whitespace()

            if index >= length:
                raise _ParseError
            if text[index] == "]":
                index += 1
                return result
            if text[index] != ",":
                raise _ParseError

            index += 1
            skip_whitespace()
            if index >= length or text[index] == "]":
                raise _ParseError

    def parse_object():
        nonlocal index
        index += 1
        result = {}
        skip_whitespace()

        if index < length and text[index] == "}":
            index += 1
            return result

        while True:
            if index >= length or text[index] != '"':
                raise _ParseError
            key = parse_string()
            skip_whitespace()

            if index >= length or text[index] != ":":
                raise _ParseError
            index += 1
            result[key] = parse_value()
            skip_whitespace()

            if index >= length:
                raise _ParseError
            if text[index] == "}":
                index += 1
                return result
            if text[index] != ",":
                raise _ParseError

            index += 1
            skip_whitespace()
            if index >= length or text[index] == "}":
                raise _ParseError

    def parse_value():
        nonlocal index
        skip_whitespace()

        if index >= length:
            raise _ParseError

        char = text[index]

        if char == '"':
            return parse_string()
        if char == "[":
            return parse_array()
        if char == "{":
            return parse_object()
        if char == "-" or char.isdigit():
            return parse_number()

        literals = {
            "true": True,
            "false": False,
            "null": None,
        }
        for literal, value in literals.items():
            if text.startswith(literal, index):
                index += len(literal)
                return value

        raise _ParseError

    try:
        value = parse_value()
        skip_whitespace()
        if index != length:
            raise _ParseError
        return value
    except (_ParseError, RecursionError):
        return None
