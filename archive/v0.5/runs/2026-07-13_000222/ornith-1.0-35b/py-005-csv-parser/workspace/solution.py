def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    at_field_start = True
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check next character for escaped quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Escaped quote
                    current_field += '"'
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    at_field_start = False
                    i += 1
                    # Validate next character if exists
                    if i < len(text):
                        next_char = text[i]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError(f"Invalid character after closing quote: {next_char}")
            elif char == '\n' or char == '\r':
                # Newline inside quotes - this is allowed
                if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                    current_field += '\r\n'
                    i += 2
                else:
                    current_field += char
                    i += 1
            else:
                current_field += char
                at_field_start = False
                i += 1
        else:
            if char == '"' and at_field_start:
                # Start of quoted field - only valid at start of field
                in_quotes = True
                at_field_start = False
                i += 1
            elif char == ',':
                # Field separator
                current_record.append(current_field)
                current_field = ""
                at_field_start = True
                i += 1
            elif char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # Record separator \r\n
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                at_field_start = True
                i += 2
            elif char == '\n':
                # Record separator \n
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                at_field_start = True
                i += 1
            else:
                current_field += char
                at_field_start = False
                i += 1
    
    # Handle last field/record, but not if input ends with newline
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    # Check if the input ends with a newline (or \r\n)
    ends_with_newline = False
    if len(text) >= 2 and text[-2:] == '\r\n':
        ends_with_newline = True
    elif text[-1] == '\n':
        ends_with_newline = True
    
    if not ends_with_newline:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
