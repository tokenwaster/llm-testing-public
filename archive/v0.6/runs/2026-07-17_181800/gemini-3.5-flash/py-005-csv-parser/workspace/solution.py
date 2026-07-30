def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    n = len(text)
    i = 0

    while i < n:
        current_record = []
        while True:
            if i < n and text[i] == '"':
                # Quoted field
                i += 1  # consume opening quote
                field_chars = []
                closed = False
                while i < n:
                    if text[i] == '"':
                        if i + 1 < n and text[i+1] == '"':
                            field_chars.append('"')
                            i += 2
                        else:
                            # Closing quote
                            i += 1
                            closed = True
                            break
                    else:
                        field_chars.append(text[i])
                        i += 1
                if not closed:
                    raise ValueError("Unclosed quoted field")

                # Check what follows the closing quote
                if i < n:
                    if text[i] == ',':
                        pass
                    elif text[i] == '\n':
                        pass
                    elif text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                        pass
                    else:
                        raise ValueError("Characters after closing quote")
                field_val = "".join(field_chars)
            else:
                # Unquoted field
                field_chars = []
                while i < n:
                    if text[i] == ',':
                        break
                    if text[i] == '\n':
                        break
                    if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                        break
                    field_chars.append(text[i])
                    i += 1
                field_val = "".join(field_chars)

            current_record.append(field_val)

            if i >= n:
                break
            elif text[i] == ',':
                i += 1
            elif text[i] == '\n':
                i += 1
                break
            elif text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                i += 2
                break
            else:
                raise ValueError("Unexpected character after field")

        records.append(current_record)

    return records
