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
        if char == '"':
            return parse_string()
        elif char in ['[', '{']:
            return parse_container()
        elif char.isdigit() or char == '-':
            return parse_number()
        elif char == 't' and i < len(text) and text[i:i+4] == 'true':
            return True
        elif char == 'f' and i < len(text) and text[i:i+5] == 'false':
            return False
        elif char == 'n' and i < len(text) and text[i:i+4] == 'null':
            return None
        elif char == ']':
            return ']'
        elif char == '}':
            return '}'
        elif char == ',':
            return ','
        elif char == ':':
            return ':'
        else:
            return None

    def parse_string():
        start = i
        while i < len(text) and text[i] != '"':
            i += 1
        if i >= len(text):
            return None
        value = text[start+1:i]
        i += 1
        return value

    def parse_container():
        result = []
        token = next_token()
        while token != ']' and token != '}':
            if token is None:
                return None
            if token == ',':
                result.append(None)
            elif token == ']':
                break
            else:
                result.append(parse_element())
            token = next_token()
        if token is None:
            return None
        if token == ']':
            return result
        elif token == '}':
            return {'**' + ''.join([str(x) for x in result]) + '**'}

    def parse_element():
        token = next_token()
        if token is None:
            return None
        if token == '"':
            return parse_string()
        elif token.isdigit() or token[0] == '-':
            return parse_number()
        elif token in ['true', 'false', 'null']:
            return eval(token)  # Use eval for boolean/null values
        else:
            return None

    def parse_number():
        start = i
        while i < len(text) and (text[i].isdigit() or text[i] == '.' or text[i] == '-'):
            i += 1
        value = text[start:i]
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return None

    result = next_token()
    if result is None:
        return None

    return result
