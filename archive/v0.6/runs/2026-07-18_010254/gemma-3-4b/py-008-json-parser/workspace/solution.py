def parse(text: str) -> object | None:
    """Parses a JSON document and returns the equivalent Python object.

    Args:
        text: The JSON string to parse.

    Returns:
        The parsed Python object, or None if the input is not valid JSON.
    """
    i = 0
    def next_token():
        nonlocal i
        while i < len(text) and text[i] == ' ':
            i += 1
        if i >= len(text):
            return None
        char = text[i]
        i += 1
        if char in ['{', '[', '(', '"', '\\', '/', '\b', '\f', '\n', '\r', '\t', 'u']:
            return char
        elif char.isdigit() or char == '-':
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                j += 1
            if j > i:
                return int(text[i:j])
        elif char == 't' and text[i:i+4] == 'true':
            return True
        elif char == 'f' and text[i:i+5] == 'false':
            return False
        elif char == 'n' and text[i:i+4] == 'null':
            return None
        elif char == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                j += 1
            if j < len(text):
                return text[i+1:j]
            else:
                return None  # Unterminated string
        elif char == '\\':
            j = i + 1
            while j < len(text):
                if text[j] == '\\':
                    j += 1
                else:
                    break
            if j < len(text):
                return text[i:j+1]
            else:
                return None # Invalid escape sequence
        elif char == 'u' and i + 3 < len(text) and all(c in '\u0000-\uFFFF' for c in text[i+1:i+4]):
            try:
                return chr(int(text[i+1:i+4], 16))
            except ValueError:
                return None # Invalid unicode escape
        else:
            return None

    def parse_value():
        token = next_token()
        if token is None:
            return None
        if isinstance(token, str):
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            else:
                return None  # Invalid string
        elif isinstance(token, int) or isinstance(token, float):
            return token
        elif token is True or token is False or token is None:
            return token
        else:
            return None

    result = parse_value()
    if next_token() is not None:
        return None  # Trailing garbage

    return result
