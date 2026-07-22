def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record = []
    current_field = ''
    in_quote = False
    i = 0
    while i < len(text):
        c = text[i]
        if in_quote:
            if c == '"':
                if i + 1 < len(text) and text[i+1] == '"':
                    # Escaped double quote
                    current_field += '"'
                    i += 2
                else:
                    # Closing quote, check what follows
                    in_quote = False
                    if i + 1 >= len(text):
                        pass  # Valid end of input
                    else:
                        next_char = text[i+1]
                        valid_next = (next_char == ',') or (next_char == '\n')
                        if next_char == '\r':
                            if i + 2 < len(text) and text[i+2] == '\n':
                                valid_next = True
                            else:
                                valid_next = False
                        if not valid_next:
                            raise ValueError("Invalid CSV: invalid data after closing quote")
                    i += 1
            else:
                current_field += c
                i += 1
        else:
            if c == ',':
                current_record.append(current_field)
                current_field = ''
                i += 1
            elif c == '\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ''
                i += 1
            elif c == '\r':
                if i + 1 < len(text) and text[i+1] == '\n':
                    # Process \r\n as line ending
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ''
                    i += 2
                else:
                    # Treat \r as part of field
                    current_field += c
                    i += 1
            elif c == '"':
                in_quote = True
                i += 1
            else:
                current_field += c
                i += 1

    if in_quote:
        raise ValueError("Unclosed quoted field")

    if len(current_record) > 0 or current_field != '':
        current_record.append(current_field)
        records.append(current_record)

    return records
