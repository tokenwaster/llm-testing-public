def parse_csv(text: str) -> list[list[str]]:
    result = []
    current_record = []
    current_field = ''
    in_quotes = False
    i = 0

    while i < len(text):
        if in_quotes:
            c = text[i]
            if c == '"':
                if i + 1 < len(text) and text[i+1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    in_quotes = False
                    i += 1
            else:
                current_field += c
                i += 1
        else:
            if i < len(text):
                c = text[i]
                if c == ',':
                    current_record.append(current_field)
                    current_field = ''
                    i += 1
                elif c == '\n' or c == '\r':
                    current_record.append(current_field)
                    result.append(current_record)
                    current_record = []
                    current_field = ''
                    if c == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                        i += 2
                    else:
                        i += 1
                else:
                    if current_field == '':
                        if c == '"':
                            in_quotes = True
                            i += 1
                        else:
                            current_field += c
                            i += 1
                    else:
                        current_field += c
                        i += 1

    if not in_quotes:
        current_record.append(current_field)
        if len(current_record) > 0:
            result.append(current_record)

    if in_quotes:
        raise ValueError("Unclosed quoted field")

    while result and (len(result[-1]) == 1 and result[-1][0] == ''):
        result.pop()

    return result
