def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    i = 0
    n = len(text)
    
    while i < n:
        # Parse a field
        if text[i] == '"':
            # Quoted field
            field = ""
            i += 1  # Skip opening quote
            while i < n:
                if text[i] == '"':
                    # Could be closing quote or escaped quote
                    if i + 1 < n and text[i + 1] == '"':
                        # Escaped quote (doubled quote)
                        field += '"'
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        break
                else:
                    field += text[i]
                    i += 1
            else:
                # Reached end of text without closing quote
                raise ValueError("Unclosed quote in field")
            
            # After closing quote, check what comes next
            if i < n:
                if text[i] == ',':
                    pass  # Will handle comma below
                elif text[i] == '\r' or text[i] == '\n':
                    pass  # Will handle newline below
                else:
                    raise ValueError("Characters after closing quote")
        else:
            # Unquoted field
            field = ""
            while i < n and text[i] not in [',', '\n', '\r']:
                field += text[i]
                i += 1
        
        current_record.append(field)
        
        # Check what comes after the field
        if i < n:
            if text[i] == ',':
                i += 1
            elif text[i] == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                records.append(current_record)
                current_record = []
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
    
    # Add the last record if there's content
    if current_record:
        records.append(current_record)
    
    return records
