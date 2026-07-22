def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i < n:
        # Check if we are at a field starting with a quote
        if text[i] == '"':
            # Quoted field
            i += 1  # consume opening quote
            field_chars = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        closed = True
                        i += 1  # consume closing quote
                        break
                else:
                    field_chars.append(text[i])
                    i += 1
            
            if not closed:
                raise ValueError("Unclosed quoted field")
            
            current_record.append("".join(field_chars))
            
            # After a closing quote, we must find a comma, a newline, or EOF
            if i < n:
                if text[i] == ',':
                    i += 1
                    # If the comma is at the very end of the text, it means a trailing empty field
                    if i == n:
                        current_record.append("")
                elif text[i] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 1
                elif text[i] == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    records.append(current_record)
                    current_record = []
                else:
                    raise ValueError("Extra characters after closing quote")
        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\r', '\n'):
                field_chars.append(text[i])
                i += 1
            
            current_record.append("".join(field_chars))
            
            if i < n:
                if text[i] == ',':
                    i += 1
                    if i == n:
                        current_record.append("")
                elif text[i] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 1
                elif text[i] == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    records.append(current_record)
                    current_record = []

    # If we finished processing and there is a pending record, add it.
    # Note: A trailing newline at the end of the input does not create an extra record.
    # If current_record is empty, it means the last thing we saw was a newline,
    # so we don't add an extra empty record.
    if current_record:
        records.append(current_record)
        
    return records
