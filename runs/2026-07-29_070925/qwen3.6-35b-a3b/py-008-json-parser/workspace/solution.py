def parse(text: str):
    pos = 0
    length = len(text)

    def peek():
        return text[pos] if pos < length else None

    def advance():
        nonlocal pos
        if pos >= length:
            raise ValueError("Unexpected end")
        ch = text[pos]
        pos += 1
        return ch

    def skip_ws():
        nonlocal pos
        while pos < length and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        skip_ws()
        if pos >= length:
            raise ValueError("Unexpected end")
        ch = peek()
        if ch == '"':
            return parse_string()
        elif ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == 't':
            return parse_true()
        elif ch == 'f':
            return parse_false()
        elif ch == 'n':
            return parse_null()
        elif ch == '-' or ch.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {ch!r}")

    def parse_string():
        if advance() != '"':
            raise ValueError("Expected '\"'")
        s = []
        while True:
            if pos >= length:
                raise ValueError("Unterminated string")
            ch = text[pos]
            if ch == '"':
                pos += 1
                return ''.join(s)
            elif ch == '\\':
                pos += 1
                if pos >= length:
                    raise ValueError("Unterminated escape")
                esc = text[pos]
                if esc == '"':
                    s.append('"')
                elif esc == '\\':
                    s.append('\\')
                elif esc == '/':
                    s.append('/')
                elif esc == 'b':
                    s.append('\b')
                elif esc == 'f':
                    s.append('\f')
                elif esc == 'n':
                    s.append('\n')
                elif esc == 'r':
                    s.append('\r')
                elif esc == 't':
                    s.append('\t')
                elif esc == 'u':
                    if length - pos < 5:
                        raise ValueError("Incomplete unicode escape")
                    hex_str = text[pos+1:pos+5]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ValueError("Invalid hex in unicode escape")
                    try:
                        s.append(chr(int(hex_str, 16)))
                    except ValueError:
                        raise ValueError("Invalid unicode code point")
                    pos += 4
                else:
                    raise ValueError(f"Invalid escape character: {esc!r}")
                pos += 1
            elif ord(ch) < 0x20:
                raise ValueError("Control character in string")
            else:
                s.append(ch)
                pos += 1

    def parse_number():
        start_pos = pos
        if peek() == '-':
            advance()
        
        if pos >= length:
            raise ValueError("Unexpected end of number")
        ch = text[pos]
        if ch == '0':
            advance()
            if pos < length and text[pos].isdigit():
                raise ValueError("Leading zero not allowed")
        else:
            while pos < length and text[pos].isdigit():
                advance()
                
        is_float = False
        if pos < length and text[pos] == '.':
            is_float = True
            advance()
            if pos >= length or not text[pos].isdigit():
                raise ValueError("Expected digit after decimal point")
            while pos < length and text[pos].isdigit():
                advance()
                
        exp_start = False
        if pos < length and text[pos] in ('e', 'E'):
            exp_start = True
            advance()
            if pos < length and text[pos] in ('+', '-'):
                advance()
            if pos >= length or not text[pos].isdigit():
                raise ValueError("Expected digit in exponent")
            while pos < length and text[pos].isdigit():
                advance()
                
        num_str = text[start_pos:pos]
        try:
            if exp_start or is_float:
                return float(num_str)
            else:
                return int(num_str)
        except:
            raise ValueError("Invalid number")

    def parse_object():
        if advance() != '{':
            raise ValueError("Expected '{'")
        skip_ws()
        result = {}
        if pos < length and peek() == '}':
            pos += 1
            return result
            
        while True:
            key = parse_string()
            skip_ws()
            if pos >= length or peek() != ':':
                raise ValueError("Expected ':'")
            advance()
            skip_ws()
            value = parse_value()
            result[key] = value
            
            skip_ws()
            if pos < length and peek() == ',':
                advance()
                continue
            elif pos < length and peek() == '}':
                pos += 1
                return result
            else:
                raise ValueError("Expected ',' or '}' in object")

    def parse_array():
        if advance() != '[':
            raise ValueError("Expected '['")
        skip_ws()
        result = []
        if pos < length and peek() == ']':
            pos += 1
            return result
            
        while True:
            value = parse_value()
            result.append(value)
            
            skip_ws()
            if pos < length and peek() == ',':
                advance()
                continue
            elif pos < length and peek() == ']':
                pos += 1
                return result
            else:
                raise ValueError("Expected ',' or ']' in array")

    def parse_true():
        if length - pos >= 4 and text[pos:pos+4] == 'true':
            nonlocal pos
            pos += 4
            return True
        raise ValueError("Invalid literal")

    def parse_false():
        if length - pos >= 5 and text[pos:pos+5] == 'false':
            nonlocal pos
            pos += 5
            return False
        raise ValueError("Invalid literal")

    def parse_null():
        if length - pos >= 4 and text[pos:pos+4] == 'null':
            nonlocal pos
            pos += 4
            return None
        raise ValueError("Invalid literal")

    try:
        result = parse_value()
        skip_ws()
        if pos != length:
            return None # trailing garbage
        return result
    except:
        return None
