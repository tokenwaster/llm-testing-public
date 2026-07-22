def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check if it's a doubled quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2  # Skip both quotes
                    continue
                else:
                    # End of quoted field - validate what comes next
                    in_quotes = False
                    i += 1
                    
                    # After closing quote, we should have comma, newline, or EOF
                    if i < len(text):
                        next_char = text[i]
                        if next_char not in [',', '\n', '\r']:
                            raise ValueError("Invalid characters after closing quote")
                        # Handle \r\n case
                        if next_char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                            i += 2
                        elif next_char in ['\n', '\r']:
                            i += 1
                    continue
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                # Start of quoted field - only valid at beginning of field
                in_quotes = True
                i += 1
            elif char == ',':
                # End of field
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\r':
                # Handle \r\n or standalone \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2  # Skip both characters
                else:
                    i += 1
                
                # End of record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            elif char == '\n':
                # End of record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += char
                i += 1
    
    # Handle case where file doesn't end with newline
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field and record if we have data
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
