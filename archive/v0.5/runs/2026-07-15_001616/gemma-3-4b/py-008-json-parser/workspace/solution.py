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
        if char in ('"', '\\', '/', '\b', '\f', '\n', '\r', '\t'):
            j = i
            while i < len(text) and text[i] != char:
                if text[i] == '\\':
                    i += 2
                else:
                    i += 1
            if i >= len(text):
                return None
            return text[j:i], i
        elif char.isdigit() or char == '-':
            num_str = ''
            while i < len(text) and (text[i].isdigit() or text[i] == '.' or text[i] == 'e' or text[i] == '+' or text[i] == '-'):
                num_str += text[i]
                i += 1
            try:
                if num_str.count('.') > 1:
                    return None
                num = float(num_str)
                if num == int(num):
                    return int(num), i
                else:
                    return num, i
            except ValueError:
                return None, i
        elif char == 't' or char == 'f' or char == 'n':
            return bool_val(char), i
        elif char == '{':
            obj = {}
            while i < len(text):
                token, i = next_token()
                if token is None:
                    return None, i
                if token.endswith(':'):
                    key, i = next_token()
                    if key is None:
                        return None, i
                    value, i = next_token()
                    if value is None:
                        return None, i
                    obj[key] = value
                else:
                    return None, i
            return obj, i
        elif char == '[':
            arr = []
            while i < len(text):
                token, i = next_token()
                if token is None:
                    return None, i
                if token.endswith(']'):
                    arr.append(token[:-1])
                    i += 1
                else:
                    arr.append(token)
            return arr, i
        else:
            return None, i

    def bool_val(char):
        if char == 't':
            return True
        elif char == 'f':
            return False
        else:
            return None

    result, i = next_token()
    if result is None:
        return None
    if i < len(text):
        return None
    return result
