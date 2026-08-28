def parse(text: str):
    index = 0
    length = len(text)

    def skip_whitespace():
        nonlocal index
        while index < length and text[index] in " \t\r\n":
            index += 1

    def parse_value():
        nonlocal index
        skip_whitespace()

        if index >= length:
            raise ValueError

        char = text[index]

        if char == '"':
            return parse_string()
        if char == "{":
            return parse_object()
        if char == "[":
            return parse_array()
        if char == "t" and text[index:index + 4] == "true":
            index += 4
            return True
        if char == "f" and text[index:index + 5] == "false":
            index += 5
            return False
        if char == "n" and text[index:index + 4] == "null":
            index += 4
            return None
        if char == "-" or char.isdigit():
            return parse_number()

        raise ValueError

    def parse_string():
        nonlocal index
        if text[index] != '"':
            raise ValueError

        index += 1
        result = []

        while index < length:
            char = text[index]
            index += 1

            if char == '"':
                return "".join(result)

            if ord(char) < 0x20:
                raise ValueError

            if char != "\\":
                result.append(char)
                continue

            if index >= length:
                raise ValueError

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
            elif escape == "u":
                if index + 4 > length:
                    raise ValueError
                digits = text[index:index + 4]
                if any(c not in "0123456789abcdefABCDEF" for c in digits):
                    raise ValueError
                index += 4
                codepoint = int(digits, 16)

                if 0xD800 <= codepoint <= 0xDBFF:
                    if text[index:index + 2] != "\\u":
                        raise ValueError
                    index += 2
                    if index + 4 > length:
                        raise ValueError
                    low_digits = text[index:index + 4]
                    if any(c not in "0123456789abcdefABCDEF" for c in low_digits):
                        raise ValueError
                    index += 4
                    low = int(low_digits, 16)
                    if not 0xDC00 <= low <= 0xDFFF:
                        raise ValueError
                    codepoint = 0x10000 + ((codepoint - 0xD800) << 10) + (low - 0xDC00)
                elif 0xDC00 <= codepoint <= 0xDFFF:
                    raise ValueError

                result.append(chr(codepoint))
            else:
                raise ValueError

        raise ValueError

    def parse_number():
        nonlocal index
        start = index

        if text[index] == "-":
            index += 1
            if index >= length:
                raise ValueError

        if index >= length or not text[index].isdigit():
            raise ValueError

        if text[index] == "0":
            index += 1
            if index < length and text[index].isdigit():
                raise ValueError
        else:
            while index < length and text[index].isdigit():
                index += 1

        is_float = False

        if index < length and text[index] == ".":
            is_float = True
            index += 1
            fraction_start = index
            while index < length and text[index].isdigit():
                index += 1
            if index == fraction_start:
                raise ValueError

        if index < length and text[index] in "eE":
            is_float = True
            index += 1
            if index < length and text[index] in "+-":
                index += 1
            exponent_start = index
            while index < length and text[index].isdigit():
                index += 1
            if index == exponent_start:
                raise ValueError

        value = text[start:index]
        return float(value) if is_float else int(value)

    def parse_array():
        nonlocal index
        index += 1
        skip_whitespace()

        result = []
        if index < length and text[index] == "]":
            index += 1
            return result

        while True:
            result.append(parse_value())
            skip_whitespace()

            if index >= length:
                raise ValueError
            if text[index] == "]":
                index += 1
                return result
            if text[index] != ",":
                raise ValueError

            index += 1
            skip_whitespace()
            if index >= length or text[index] == "]":
                raise ValueError

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
                raise ValueError

            key = parse_string()
            skip_whitespace()

            if index >= length or text[index] != ":":
                raise ValueError
            index += 1

            result[key] = parse_value()
            skip_whitespace()

            if index >= length:
                raise ValueError
            if text[index] == "}":
                index += 1
                return result
            if text[index] != ",":
                raise ValueError

            index += 1
            skip_whitespace()
            if index >= length or text[index] == "}":
                raise ValueError

    try:
        value = parse_value()
        skip_whitespace()
        return value if index == length else None
    except (ValueError, OverflowError):
        return None
