def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record_fields = []
    current_field = ''
    in_quotes = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            # Check for escaped quote
            if in_quotes and i + 1 < len(text) and text[i+1] == '"':
                current_field += '"'
                i += 2
            else:
                in_quotes = not in_quotes
                i += 1
        elif c == ',':
            if in_quotes:
                current_field += ','
                i += 1
            else:
                current_record_fields.append(current_field)
                current_field = ''
                i += 1
        elif c in '\r\n':
            # Handle line break
            if in_quotes:
                current_field += c
                if c == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                current_record_fields.append(current_field)
                # Add the record
                records.append(current_record Fields)
                current_record_fields = []
                current_field = ''
                # Handle line break
                if c == '\r':
                    if i + 1 < len(text) and text[i+1] == '\n':
                        i += 2
                    else:
                        i += 1
                elif c == '\n':
                    i += 1
        else:
            current_field += c
            i += 1

    # After processing all characters, check if in_quotes
    if in_quotes:
        raise ValueError("Unclosed quoted field")

    # Add any remaining current_field to the last record
    if current_field or current_record_fields:
        current_record_fields.append(current_field)
        records.append(current_record_fields)

    return records
