def parse(text: str):
    pos = [0]
    
    def skip_whitespace():
        nonlocal pos
        while pos[0] < len(text) and text[pos[0]].isspace():
            pos[0] += 1
    
    def error():
        return None
    
    def parse_value():
        nonlocal pos
        skip_whitespace()
        if pos[0] >= len(text):
            return None
        c = text[pos[0]]
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c == 't':
            skip_whitespace()
            if pos[0] + 3 < len(text) and text[pos[0]:pos[0]+4] == 'true':
                pos[0] += 4
                return True
            else:
                return None
        elif c == 'f':
            skip_whitespace()
            if pos[0] + 4 < len(text) and text[pos[0]:pos[0]+5] == 'false':
                pos[0] += 5
                return False
            else:
                return None
        elif c == 'n':
            skip_whitespace()
            if pos[0] + 3 < len(text) and text[pos[0]:pos[0]+4] == 'null':
                pos[0] += 4
                return None
            else:
                return None
        elif c in '-0123456789':
            return parse_number()
        else:
            return None
    
    def parse_string():
        nonlocal pos
        start = pos[0]
        pos[0] += 1  # skip opening "
        s = []
        while pos[0] < len(text):
            c = text[pos[0]]
            if c == '"':
                pos[0] += 1
                return ''.join(s)
            elif c == '\\':
                pos[0] += 1  # move past backslash
                if pos[0] >= len(text):
                    return None
                escape_char = text[pos[0]]
                if escape_char == '"':
                    s.append('"')
                    pos[0] += 1
                elif escape_char == '\\':
                    s.append('\\')
                    pos[0] += 1
                elif escape_char == '/':
                    s.append('/')
                    pos[0] += 1
                elif escape_char == 'b':
                    s.append('\b')
                    pos[0] += 1
                elif escape_char == 'f':
                    s.append('\f')
                    pos[0] += 1
                elif escape_char == 'n':
                    s.append('\n')
                    pos[0] += 1
                elif escape_char == 'r':
                    s.append('\r')
                    pos[0] += 1
                elif escape_char == 't':
                    s.append('\t')
                    pos[0] += 1
                elif escape_char == 'u':
                    if pos[0] +4 >= len(text):
                        return None
                    hex_str = text[pos[0]+1 : pos[0]+5]
                    try:
                        code_point = int(hex_str, 16)
                    except ValueError:
                        return None
                    s.append(chr(code_point))
                    pos[0] += 5
                else:
                    return None
            else:
                s.append(c)
                pos[0] += 1
        # Unterminated string
        return None
    
    def parse_object():
        nonlocal pos
        skip_whitespace()
        if text[pos[0]] != '{':
            return None
        pos[0] += 1
        result = {}
        while True:
            skip_whitespace()
            if pos[0] >= len(text):
                return None
            if text[pos[0]] == '}':
                pos[0] += 1
                return result
            key = parse_string()
            if key is None:
                return None
            skip_whitespace()
            if pos[0] >= len(text) or text[pos[0]] != ':':
                return None
            pos[0] += 1  # consume colon
            value = parse_value()
            if value is None:
                return None
            result[key] = value
            skip_whitespace()
            if pos[0] >= len(text):
                return None
            if text[pos[0]] == ',':
                pos[0] += 1
            elif text[pos[0]] == '}':
                pos[0] += 1
                break
            else:
                return None
        return result
    
    def parse_array():
        nonlocal pos
        skip_whitespace()
        if text[pos[0]] != '[':
            return None
        pos[0] += 1
        result = []
        while True:
            skip_whitespace()
            if pos[0] >= len(text):
                return None
            if text[pos[0]] == ']':
                pos[0] += 1
                return result
            value = parse_value()
            if value is None:
                return None
            result.append(value)
            skip_whitespace()
            if pos[0] >= len(text):
                return None
            if text[pos[0]] == ',':
                pos[0] += 1
            elif text[pos[0]] == ']':
                pos[0] += 1
                break
            else:
                return None
        return result
    
    def parse_number():
        nonlocal pos
        start = pos[0]
        # Check for sign
        negative = False
        if text[pos[0]] == '-':
            negative = True
            pos[0] += 1
        # Parse integer part
        if pos[0] >= len(text) or not text[pos[0]].isdigit():
            return None
        if text[pos[0]] == '0':
            pos[0] += 1
            # Check for more digits after zero (invalid)
            if pos[0] < len(text) and text[pos[0]].isdigit():
                return None
        else:
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        # Parse fractional part
        if pos[0] < len(text) and text[pos[0]] == '.':
            pos[0] += 1
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        # Parse exponent
        if pos[0] < len(text) and text[pos[0]] in 'eE':
            pos[0] += 1
            # Optional sign
            if pos[0] < len(text) and text[pos[0]] in '+-':
                pos[0] += 1
            # Must have digits
            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                return None
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        # Construct number string
        end = pos[0]
        num_str = text[start:end]
        try:
            if '.' in num_str or 'e' in num_str.lower():
                value = float(num_str)
            else:
                value = int(num_str)
        except (ValueError, OverflowError):
            return None
        return value
    
    # Main parsing logic
    skip_whitespace()
    result = parse_value()
    if result is not None:
        skip_whitespace()
        if pos[0] != len(text):  # trailing characters?
            return None
    return result
