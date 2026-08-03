def parse(text: str) -> object:
    """Parses a JSON document and returns the equivalent Python object.

    Args:
        text: The JSON string to parse.

    Returns:
        The parsed Python object, or None if the input is not valid JSON.
    """
    tokens = tokenize(text)
    if tokens is None:
        return None

    def parse_value():
        assert isinstance(tokens, list)
        token = tokens.pop(0)
        if token == '{':
            return parse_object()
        elif token == '[':
            return parse_array()
        elif token == 'true':
            return True
        elif token == 'false':
            return False
        elif token == 'null':
            return None
        elif token.isdigit() or token[0] == '-': \
                and token[1:].isdigit() or token.startswith('0x') and all(c.isdigit() or c in 'ABCDEFabcdef' for c in token[2:]):
            try:
                if '.' in token:
                    return float(token)
                else:
                    return int(token)
            except ValueError:
                return None
        elif isinstance(token, str):
            # Check for escaped characters
            escaped = False
            result = ''
            for char in token:
                if char == '\\' and not escaped:
                    escaped = True
                else:
                    escaped = False
                if escaped:
                    result += char
                else:
                    result += char
            return result
        else:
            return None

    def parse_object():
        obj = {}
        while tokens and tokens[0] != '}':
            assert isinstance(tokens, list)
            key = parse_string()
            if key is None:
                return None
            if not isinstance(tokens, list):
                return None

            if tokens[0] != ':':
                return None

            value = parse_value()
            if value is None:
                return None
            obj[key] = value
            while tokens and (tokens[0] == ',' or tokens[0] == '}'):
                tokens.pop(0)
        assert isinstance(tokens, list)
        if tokens[0] != '}':
            return None
        tokens.pop(0)
        return obj

    def parse_array():
        arr = []
        while tokens and tokens[0] != ']':
            assert isinstance(tokens, list)
            value = parse_value()
            if value is None:
                return None
            arr.append(value)
            while tokens and (tokens[0] == ',' or tokens[0] == ']'):
                tokens.pop(0)
        assert isinstance(tokens, list)
        if tokens[0] != ']':
            return None
        tokens.pop(0)
        return arr

    def parse_string():
        assert isinstance(tokens, list)
        token = tokens.pop(0)
        if token == '"':
            i = 1
            while i < len(token):
                if token[i] == '\\':
                    escaped = False
                    i += 1
                    if i >= len(token):
                        return None
                    if token[i] == 'n':
                        i += 1
                        return '\n'
                    elif token[i] == 't':
                        i += 1
                        return '\t'
                    elif token[i] == '\\':
                        i += 1
                        return '\\'
                    elif token[i] == '"':
                        i += 1
                        return '"'
                    elif token[i] == '/':
                        i += 1
                        return '/'
                    elif token[i] == 'b':
                        i += 1
                        return '\b'
                    elif token[i] == 'f':
                        i += 1
                        return '\f'
                    else:
                        i += 1
                        continue
                elif token[i] == '"':
                    return token[1:i]
                else:
                    i += 1
            return None
        else:
            return None

    result = parse_value()
    if tokens:
        return None
    return result


def tokenize(text: str) -> list | None:
    """Tokenizes a JSON string.

    Args:
        text: The JSON string to tokenize.

    Returns:
        A list of tokens, or None if the input is not valid JSON.
    """
    tokens = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in '\",\t\n\r\\{}[]':
            tokens.append(char)
            i += 1
        elif char.isdigit() or char == '-':
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                j += 1
            try:
                if '.' in text[i:j]:
                    tokens.append(text[i:j])
                else:
                    tokens.append(int(text[i:j]))
                i = j
            except ValueError:
                return None
        elif char == '[' or char == ']' or char == '{' or char == '}':
            tokens.append(char)
            i += 1
        elif char == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                j += 1
            if j >= len(text):
                return None
            tokens.append(text[i:j+1])
            i = j + 1
        elif char == 't' and i+3 < len(text) and text[i+1:i+4] == 'rue':
            tokens.append('true')
            i += 4
        elif char == 'f' and i+4 < len(text) and text[i+1:i+5] == 'false':
            tokens.append('false')
            i += 5
        elif char == 'n' and i+3 < len(text) and text[i+1:i+4] == 'ull':
            tokens.append('null')
            i += 4
        else:
            return None
    return tokens
