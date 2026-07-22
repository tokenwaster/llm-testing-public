def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record_fields = []
    current_field = ''
    in_quotes = False
    i = 0
    while i < len(text):
        if in_quotes:
            if text[i] == '"':
                # Check for escaped quote
                if i + 1 < len(text) and text[i+1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
            else:
                current_field += text[i]
                i += 1
        else:
            if text[i] == ',':
                current_record_fields.append(current_field)
                current_field = ''
                i += 1
            elif text[i] == '\r':
                # Check for CRLF line break
                if i + 1 < len(text) and text[i+1] == '\n':
                    current_record_fields.append(current_field)
                    records.append(current_record_fields)
                    current_record_fields = []
                    current_field = ''
                    i += 2
                else:
                    # Single \r, treat as record separator
                    current_record_fields.append(current_field)
                    records.append(current_record_fields)
                    current_record_fields = []
                    current_field = ''
                    i += 1
            elif text[i] == '\n':
                current_record_fields.append(current_field)
                records.append(current_record_fields)
                current_record_fields = []
                current_field = ''
                i += 1
            else:
                if text[i] == '"':
                    in_quotes = True
                current_field += text[i]
                i += 1

    # After processing all characters, add the last field and record if needed
    if not in_quotes:
        current_record_fields.append(current_field)
        if len(current_record_fields) > 0 or (len(current_record_fields) == 1 and current_record_fields[0] == ''):
            records.append(current_record_fields)
    else:
        raise ValueError("Unclosed quoted field")

    # Check for empty lines in the middle
    final_records = []
    for record in records:
        if len(record) == 0:
            final_records.append([''])
        else:
            final_records.append(record)

    return final_records
