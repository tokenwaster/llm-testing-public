def parse(text: str):
    """Parse a JSON document and return the equivalent Python object."""
    try:
        pos, result = _parse_value(text, 0)
        # Check that we've consumed the entire input (except trailing whitespace)
        pos = _skip_whitespace(text, pos)
        if pos != len(text):
            return None
        return result
    except:
        return None


def _skip_whitespace(text: str, pos: int) -> int:
    """Skip whitespace and return the new position."""
    while pos < len(text) and text[pos] in ' \t\n\r':
        pos += 1
    return pos


def _parse_value(text: str, pos: int) -> tuple:
    """Parse a JSON value and return (new_pos, value)."""
    pos = _skip_whitespace(text, pos)
    
    if pos >= len(text):
        raise ValueError("Unexpected end of input")
    
    ch = text[pos]
    
    if ch == '{':
        return _parse_object(text, pos)
    elif ch == '[':
        return _parse_array(text, pos)
    elif ch == '"':
        return _parse_string(text, pos)
    elif ch == 't':
        return _parse_literal(text, pos, 'true', True)
    elif ch == 'f':
        return _parse_literal(text, pos, 'false', False)
    elif ch == 'n':
        return _parse_literal(text, pos, 'null', None)
    elif ch == '-' or ch.isdigit():
        return _parse_number(text, pos)
    else:
        raise ValueError(f"Unexpected character: {ch}")


def _parse_object(text: str, pos: int) -> tuple:
    """Parse a JSON object."""
    pos += 1  # skip '{'
    pos = _skip_whitespace(text, pos)
    
    obj = {}
    
    # Empty object
    if pos < len(text) and text[pos] == '}':
        return pos + 1, obj
    
    while True:
        pos = _skip_whitespace(text, pos)
        
        # Parse key (must be string)
        if pos >= len(text) or text[pos] != '"':
            raise ValueError("Expected string key in object")
        
        pos, key = _parse_string(text, pos)
        
        pos = _skip_whitespace(text, pos)
        
        # Expect colon
        if pos >= len(text) or text[pos] != ':':
            raise ValueError("Expected ':' after object key")
        
        pos += 1
        
        # Parse value
        pos, value = _parse_value(text, pos)
        
        obj[key] = value
        
        pos = _skip_whitespace(text, pos)
        
        if pos >= len(text):
            raise ValueError("Unterminated object")
        
        if text[pos] == '}':
            return pos + 1, obj
        elif text[pos] == ',':
            pos += 1
        else:
            raise ValueError("Expected ',' or '}' in object")


def _parse_array(text: str, pos: int) -> tuple:
    """Parse a JSON array."""
    pos += 1  # skip '['
    pos = _skip_whitespace(text, pos)
    
    arr = []
    
    # Empty array
    if pos < len(text) and text[pos] == ']':
        return pos + 1, arr
    
    while True:
        # Parse value
        pos, value = _parse_value(text, pos)
        arr.append(value)
        
        pos = _skip_whitespace(text, pos)
        
        if pos >= len(text):
            raise ValueError("Unterminated array")
        
        if text[pos] == ']':
            return pos + 1, arr
        elif text[pos] == ',':
            pos += 1
        else:
            raise ValueError("Expected ',' or ']' in array")


def _parse_string(text: str, pos: int) -> tuple:
    """Parse a JSON string."""
    pos += 1  # skip opening '"'
    result = []
    
    while pos < len(text):
        ch = text[pos]
        
        if ch == '"':
            return pos + 1, ''.join(result)
        elif ch == '\\':
            pos += 1
            if pos >= len(text):
                raise ValueError("Unterminated string escape")
            
            escape_ch = text[pos]
            if escape_ch == '"':
                result.append('"')
            elif escape_ch == '\\':
                result.append('\\')
            elif escape_ch == '/':
                result.append('/')
            elif escape_ch == 'b':
                result.append('\b')
            elif escape_ch == 'f':
                result.append('\f')
            elif escape_ch == 'n':
                result.append('\n')
            elif escape_ch == 'r':
                result.append('\r')
            elif escape_ch == 't':
                result.append('\t')
            elif escape_ch == 'u':
                # Unicode escape
                if pos + 4 >= len(text):
                    raise ValueError("Incomplete unicode escape")
                hex_str = text[pos+1:pos+5]
                if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    raise ValueError("Invalid unicode escape")
                code_point = int(hex_str, 16)
                result.append(chr(code_point))
                pos += 4
            else:
                raise ValueError(f"Invalid escape sequence: \\{escape_ch}")
        else:
            result.append(ch)
        
        pos += 1
    
    raise ValueError("Unterminated string")


def _parse_number(text: str, pos: int) -> tuple:
    """Parse a JSON number."""
    start = pos
    
    # Optional minus
    if pos < len(text) and text[pos] == '-':
        pos += 1
    
    if pos >= len(text):
        raise ValueError("Invalid number")
    
    # Integer part
    if text[pos] == '0':
        pos += 1
        # Check for leading zeros (not allowed except '0' itself)
        if pos < len(text) and text[pos].isdigit():
            raise ValueError("Leading zeros not allowed")
    elif text[pos].isdigit():
        while pos < len(text) and text[pos].isdigit():
            pos += 1
    else:
        raise ValueError("Invalid number")
    
    is_float = False
    
    # Fractional part
    if pos < len(text) and text[pos] == '.':
        is_float = True
        pos += 1
        if pos >= len(text) or not text[pos].isdigit():
            raise ValueError("Invalid number: expected digits after '.'")
        while pos < len(text) and text[pos].isdigit():
            pos += 1
    
    # Exponent part
    if pos < len(text) and text[pos] in 'eE':
        is_float = True
        pos += 1
        if pos < len(text) and text[pos] in '+-':
            pos += 1
        if pos >= len(text) or not text[pos].isdigit():
            raise ValueError("Invalid number: expected digits in exponent")
        while pos < len(text) and text[pos].isdigit():
            pos += 1
    
    num_str = text[start:pos]
    
    if is_float:
        return pos, float(num_str)
    else:
        return pos, int(num_str)


def _parse_literal(text: str, pos: int, literal: str, value) -> tuple:
    """Parse a JSON literal (true, false, null)."""
    if text[pos:pos+len(literal)] == literal:
        return pos + len(literal), value
    else:
        raise ValueError(f"Invalid literal")
