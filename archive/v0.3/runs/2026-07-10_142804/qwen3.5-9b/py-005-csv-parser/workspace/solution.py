def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check for escaped quote (")
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # End of quoted field
                    in_quotes = False
                    current_record.append(''.join(current_field))
                    current_field = []
            elif char == '\n' or char == '\r':
                # Newline inside quoted field - keep it as part of the field
                current_field.append(char)
        else:
            if char == '"':
                # Start of a quoted field
                in_quotes = True
                current_field.append(char)
            elif char == ',':
                # End of field (not quoted)
                current_record.append(''.join(current_field))
                current_field = []
            elif char == '\n' or char == '\r':
                # End of record
                if current_field:
                    current_record.append(''.join(current_field))
                    current_field = []
                records.append(current_record)
                current_record = []
                
                # Skip \r if it was part of \r\n to avoid double counting
                if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1
            else:
                current_field.append(char)
        
        i += 1
    
    # Handle remaining content after loop
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
