import re

def parse(text: str):
    """
    Parses a JSON document and returns the equivalent Python object,
    or returns None if the input is not valid JSON.
    """
    # Regexes for tokens
    # Whitespace: space, tab, carriage return, newline
    ws_re = re.compile(r'[ \t\r\n]*')
    
    # Number regex matching strict JSON number format:
    # -? ( 0 | [1-9][0-9]* ) ( \. [0-9]+ )? ( [eE] [+-]? [0-9]+ )?
    num_re = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
    
    # String escape mappings
    escapes = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t'
    }
    
    length = len(text)
    cursor = 0

    def skip_ws():
        nonlocal cursor
        m = ws_re.match(text, cursor)
        if m:
            cursor = m.end()

    def parse_value():
        nonlocal cursor
        skip_ws()
        if cursor >= length:
            raise ValueError("Unexpected EOF")
        
        char = text[cursor]
        
        # String
        if char == '"':
            return parse_string()
        # Object
        elif char == '{':
            return parse_object()
        # Array
        elif char == '[':
            return parse_array()
        # True
        elif text.startswith('true', cursor):
            cursor += 4
            return True
        # False
        elif text.startswith('false', cursor):
            cursor += 5
            return False
        # Null
        elif text.startswith('null', cursor):
            cursor += 4
            return None
        # Number
        else:
            # Try to match a number
            m = num_re.match(text, cursor)
            if m:
                num_str = m.group(0)
                cursor += len(num_str)
                if '.' in num_str or 'e' in num_str or 'E' in num_str:
                    return float(num_str)
                else:
                    return int(num_str)
            else:
                raise ValueError("Unexpected token")

    def parse_string():
        nonlocal cursor
        # Assumes cursor points to '"'
        cursor += 1  # skip opening quote
        result = []
        while cursor < length:
            char = text[cursor]
            if char == '"':
                cursor += 1  # skip closing quote
                return "".join(result)
            elif char == '\\':
                if cursor + 1 >= length:
                    raise ValueError("Unterminated escape sequence")
                esc = text[cursor + 1]
                if esc in escapes:
                    result.append(escapes[esc])
                    cursor += 2
                elif esc == 'u':
                    if cursor + 5 >= length:
                        raise ValueError("Unterminated unicode escape")
                    hex_str = text[cursor + 2 : cursor + 6]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ValueError("Invalid unicode escape")
                    result.append(chr(int(hex_str, 16)))
                    cursor += 6
                else:
                    raise ValueError("Invalid escape character")
            elif ord(char) < 0x20:
                # Control characters must be escaped in JSON strings
                raise ValueError("Unescaped control character")
            else:
                result.append(char)
                cursor += 1
        raise ValueError("Unterminated string")

    def parse_array():
        nonlocal cursor
        cursor += 1  # skip '['
        skip_ws()
        if cursor < length and text[cursor] == ']':
            cursor += 1
            return []
        
        arr = []
        while True:
            val = parse_value()
            arr.append(val)
            skip_ws()
            if cursor >= length:
                raise ValueError("Unterminated array")
            char = text[cursor]
            if char == ']':
                cursor += 1
                return arr
            elif char == ',':
                cursor += 1
            else:
                raise ValueError("Expected ',' or ']' in array")

    def parse_object():
        nonlocal cursor
        cursor += 1  # skip '{'
        skip_ws()
        if cursor < length and text[cursor] == '}':
            cursor += 1
            return {}
        
        obj = {}
        while True:
            skip_ws()
            if cursor >= length or text[cursor] != '"':
                raise ValueError("Expected string key in object")
            key = parse_string()
            skip_ws()
            if cursor >= length or text[cursor] != ':':
                raise ValueError("Expected ':' after key in object")
            cursor += 1  # skip ':'
            val = parse_value()
            obj[key] = val
            skip_ws()
            if cursor >= length:
                raise ValueError("Unterminated object")
            char = text[cursor]
            if char == '}':
                cursor += 1
                return obj
            elif char == ',':
                cursor += 1
            else:
                raise ValueError("Expected ',' or '}' in object")

    try:
        skip_ws()
        if cursor >= length:
            return None  # Empty input is invalid JSON
        res = parse_value()
        skip_ws()
        if cursor < length:
            return None  # Trailing garbage
        return res
    except ValueError:
        return None
