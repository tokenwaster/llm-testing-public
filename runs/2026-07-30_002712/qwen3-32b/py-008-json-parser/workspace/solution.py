def parse(text: str):
    def error():
        return None
    
    index = [0]
    
    def peek_char():
        if index[0] < len(text):
            return text[index[0]]
        else:
            return None
    
    def consume_char():
        c = peek_char()
        if c is not None:
            index[0] += 1
        return c
    
    def skip_whitespace():
        while True:
            c = peek_char()
            if c is None:
                break
            elif c in ' \t\n\r':
                consume_char()
            else:
                break
    
    def parse_value():
        skip_whitespace()
        c = peek_char()
        if c is None:
            return None
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        else:
            start_pos = index[0]
            if text.startswith('true', start_pos):
                index[0] += 4
                return True
            elif text.startswith('false', start_pos):
                index[0] += 5
                return False
            elif text.startswith('null', start_pos):
                index[0] += 4
                return None
            else:
                return parse_number()
    
    def parse_string():
        consume_char()  # Consume opening quote
        s = []
        while True:
            c = consume_char()
            if c == '"':
                return ''.join(s)
            elif c == '\\':
                esc_char = consume_char()
                if not esc_char:
                    return error()
                if esc_char == 'b':
                    s.append('\b')
                elif esc_char == 'f':
                    s.append('\f')
                elif esc_char == 'n':
                    s.append('\n')
                elif esc_char == 'r':
                    s.append('\r')
                elif esc_char == 't':
                    s.append('\t')
                elif esc_char == '"':
                    s.append('"')
                elif esc_char == '\\':
                    s.append('\\')
                elif esc_char == '/':
                    s.append('/')
                elif esc_char == 'u':
                    hex_chars = []
                    for _ in range(4):
                        hc = consume_char()
                        if hc is None:
                            return error()
                        hex_chars.append(hc)
                    try:
                        code_point = int(''.join(hex_chars), 16)
                        s.append(chr(code_point))
                    except ValueError:
                        return error()
                else:
                    return error()
            elif c is None:
                return error()
            else:
                s.append(c)
    
    def parse_object():
        consume_char()  # Consume '{'
        obj = {}
        while True:
            skip_whitespace()
            if peek_char() == '}':
                consume_char()
                return obj
            key = parse_value()
            if not isinstance(key, str):
                return error()
            skip_whitespace()
            if peek_char() != ':':
                return error()
            consume_char()  # Consume ':'
            value = parse_value()
            if value is None:
                return error()
            obj[key] = value
            skip_whitespace()
            c = peek_char()
            if c == ',':
                consume_char()
            elif c == '}':
                consume_char()
                break
            else:
                return error()
        return obj
    
    def parse_array():
        consume_char()  # Consume '['
        arr = []
        while True:
            skip_whitespace()
            if peek_char() == ']':
                consume_char()
                return arr
            value = parse_value()
            if value is None:
                return error()
            arr.append(value)
            skip_whitespace()
            c = peek_char()
            if c == ',':
                consume_char()
            elif c == ']':
                consume_char()
                break
            else:
                return error()
        return arr
    
    def parse_number():
        start_pos = index[0]
        negative = False
        if peek_char() == '-':
            consume_char()
            negative = True
        # Check for digit after sign
        if peek_char() not in '0123456789':
            return error()
        first_digit = consume_char()
        if first_digit == '0':
            next_c = peek_char()
            if next_c and next_c.isdigit():
                return error()  # Leading zero followed by digit
        else:
            while True:
                c = peek_char()
                if c is not None and c.isdigit():
                    consume_char()
                else:
                    break
        # Check for decimal part
        if peek_char() == '.':
            consume_char()
            while True:
                c = peek_char()
                if c is not None and c.isdigit():
                    consume_char()
                else:
                    break
        # Check for exponent
        if peek_char() in ('e', 'E'):
            consume_char()
            # Optional sign
            if peek_char() in '+-':
                consume_char()
            # Must have digits after exponent
            if peek_char() is None or not peek_char().isdigit():
                return error()
            while True:
                c = peek_char()
                if c is not None and c.isdigit():
                    consume_char()
                else:
                    break
        end_pos = index[0]
        num_str = text[start_pos:end_pos]
        try:
            if '.' in num_str or 'e' in num_str.lower():
                number = float(num_str)
            else:
                number = int(num_str)
            if negative:
                number *= -1
            return number
        except ValueError:
            return error()
    
    result = parse_value()
    skip_whitespace()
    if index[0] != len(text):
        return None
    return result
