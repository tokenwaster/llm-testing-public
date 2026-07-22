def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check for escaped quote ("" -> ")
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                # Start of quoted field (only special if at start of field)
                in_quotes = True
                i += 1
            elif char == ',':
                # End of field, start new field
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                # End of record
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif char == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    # \r\n - skip both
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    # Just \r (treat as newline for record separator)
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 1
            else:
                current_field.append(char)
                i += 1
    
    # Handle remaining content after loop
    if current_field or in_quotes:
        current_record.append(''.join(current_field))
    
    # Check for unclosed quotes
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    return records
