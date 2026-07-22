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
                # Check if this is an escaped quote ("" -> ")
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field - check what comes after
                    in_quotes = False
                    i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                # Start of quoted field
                in_quotes = True
                current_field.append(char)
                i += 1
            elif char == ',':
                # Field separator (only outside quotes)
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n' or char == '\r':
                # Record separator
                if char == '\r' and i + 1 < n and text[i + 1] == '\n':
                    # \r\n - skip both
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 2
                else:
                    # Just \n or just \r
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
            else:
                current_field.append(char)
                i += 1
    
    # Handle the last field/record if there's content left
    if current_field:
        current_record.append(''.join(current_field))
    
    if current_record:
        records.append(current_record)
    
    return records
