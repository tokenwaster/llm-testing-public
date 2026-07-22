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
                    current_record.append(''.join(current_field))
                    current_field = []
            else:
                current_field.append(char)
        else:
            if char == '"':
                # Start of a quoted field
                in_quotes = True
                current_field.append(char)
            elif char == ',':
                # Field separator
                current_record.append(''.join(current_field))
                current_field = []
            elif char == '\n' or char == '\r':
                # Record separator
                if char == '\r' and i + 1 < n and text[i + 1] == '\n':
                    # \r\n - skip both, don't increment i again
                    pass
                else:
                    current_record.append(''.join(current_field))
                    current_field = []
                
                if not in_quotes:
                    records.append(current_record)
                    current_record = []
            
            i += 1
    
    # Handle remaining content after loop
    if current_field or (current_record and len(current_record) > 0):
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
