def parse(text: str) -> object | None:
    """Parses a JSON document and returns the equivalent Python object."""

    tokens = tokenize(text)
    if not tokens:
        return None

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == '{':
            obj = parse_object(tokens, index)
            if obj is not None:
                return obj
            else:
                index += 1  # Skip the invalid object
        elif token == '[':
            arr = parse_array(tokens, index)
            if arr is not None:
                return arr
            else:
                index += 1  # Skip the invalid array
        elif token == 't' and tokens[index+1] == 'r' and tokens[index+2] == 'u' and tokens[index+3] == 'e':
            return True
        elif token == 'f' and tokens[index+1] == 'a' and tokens[index+2] == 'l' and tokens[index+3] == 's' and tokens[index+4] == 'e':
            return False
        elif token == 'n' and tokens[index+1] == 'u' and tokens[index+2] == 'l' and tokens[index+3] == 'l':
            return None
        elif token in ['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            num = parse_number(tokens, index)
            if num is not None:
                return num
            else:
                index += 1  # Skip invalid number
        else:
            index += 1

    return None


def tokenize(text: str) -> list[str]:
    """Tokenizes a string into a list of tokens."""
    tokens = []
    i = 0
    while i < len(text):
        if text[i] in [' ', '\t', '\n']:
            i += 1
            continue
        elif text[i] == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                j += 1
            if j == len(text):
                return []  # Unterminated string
            tokens.append(text[i+1:j])
            i = j + 1
        elif text[i] == '\\':
            j = i + 1
            while j < len(text):
                if text[j] == '\\':
                    tokens.append('\\\\')
                    j += 1
                elif text[j] in ['"', '\\', 'b', 'f', 'n', 'r', 't']:
                    tokens.append(text[j])
                    j += 1
                elif text[j].islower() and text[j].isalnum():  # unicode escape
                   
                    k = j
                    while k < len(text) and text[k].isdigit():
                        k+=1

                    if k < len(text) and text[k].isalpha():
                       escape_char=text[j] + text[k]
                       tokens.append(escape_char)
                       j = k+1
                    else:
                        return [] # invalid escape 
                else:
                    j += 1

            if j == len(text):
                return []  # Unterminated escape sequence
            i = j
        elif text[i] == ':':
            tokens.append(':')
            i += 1
        elif text[i] == ',':
            tokens.append(',')
            i += 1
        elif text[i] == ']':
            tokens.append(']')
            i += 1
        elif text[i] == '}':
            tokens.append('}')
            i += 1

        else:
            return []  # Invalid character
    return tokens


def parse_object(tokens: list[str], index: int) -> object | None:
    """Parses a JSON object."""
    obj = {}
    while index < len(tokens):
        token = tokens[index]
        if token == '}':
            return obj
        elif token in ['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            num = parse_number(tokens, index)
            if num is not None:
                obj[num] = num
            else:
                return None
            index += 1
        elif token == '"':
            value = tokens[index+1]
            index += 2
            while index < len(tokens) and tokens[index] != '"':
                index += 1
            if index >= len(tokens):
               return None

            if value != "":
                 obj[value] = value  # Treat empty string as ""
            else:
                obj[""] = ""

            index+=1


        elif token == 'true':
            return True
        elif token == 'false':
            return False
        elif token == 'null':
            return None
        elif token == ',':
            index += 1
            break
        else:
            return None

    return None


def parse_array(tokens: list[str], index: int) -> object | None:
    """Parses a JSON array."""
    arr = []
    while index < len(tokens):
        token = tokens[index]
        if token == ']':
            return arr
        elif token in ['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            num = parse_number(tokens, index)
            if num is not None:
                arr.append(num)
            else:
                return None
            index += 1

        elif token == '"':
             value = tokens[index+1]
             index+=2
             while index < len(tokens) and tokens[index] != '"':
                 index+=1
             if index >= len(tokens):
               return None
             if value != "":
                arr.append(value)

             else:
              arr.append("")
             index += 1

        elif token == 'true':
            arr.append(True)
        elif token == 'false':
            arr.append(False)
        elif token == 'null':
            arr.append(None)
        elif token == ',':
            index += 1
            break
        else:
            return None

    return None


def parse_number(tokens: list[str], index: int) -> object | None:
    """Parses a number."""
    num_str = ""
    while index < len(tokens) and tokens[index] in ['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
        num_str += tokens[index]
        index += 1

    try:
        if '.' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    except ValueError:
        return None
