def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    # Normalize line endings: \r\n -> \n, standalone \r -> \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check for escaped quote ("" -> ")
                if i + 1 < n and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                    continue
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    continue
            else:
                current_field += char
        else:
            if char == '"':
                # Start of quoted field (only if at start or after comma)
                in_quotes = True
                current_field += char
            elif char == ',':
                # Field separator
                current_record.append(current_field)
                current_field = ""
            elif char == '\n':
                # Record separator
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
        i += 1
    
    # After loop: handle remaining content
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    # Add the last field and record if there's any content left
    if current_field or current_record:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
